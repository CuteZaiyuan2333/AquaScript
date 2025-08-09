/*!
AquaScript 虚拟机核心执行引擎

这个模块实现了高性能的字节码执行引擎，包括：
- 基于栈的指令执行
- 函数调用管理
- 内存管理
- 性能优化
*/

use crate::{Result, VMError, VMStats};
use crate::bytecode::{OpCode, Instruction, Bytecode};
use crate::value::Value;
use crate::function::{Function, CallFrame};
use crate::builtins::BuiltinFunction;
use rustc_hash::FxHashMap;
use std::collections::HashMap;

/// 高性能AquaScript虚拟机
pub struct AquaVM {
    /// 常量池
    constants: Vec<Value>,
    
    /// 全局变量
    globals: Vec<Value>,
    
    /// 函数表
    functions: FxHashMap<String, Function>,
    
    /// 内置函数
    builtins: FxHashMap<String, BuiltinFunction>,
    
    /// 主程序指令
    instructions: Vec<Instruction>,
    
    /// 运行时状态
    stack: Vec<Value>,
    call_stack: Vec<CallFrame>,
    pc: usize,
    
    /// 性能统计
    stats: VMStats,
    
    /// 配置选项
    config: VMConfig,
}

/// 虚拟机配置
#[derive(Debug, Clone)]
pub struct VMConfig {
    /// 最大栈大小
    pub max_stack_size: usize,
    
    /// 最大调用栈深度
    pub max_call_depth: usize,
    
    /// 是否启用性能统计
    pub enable_stats: bool,
    
    /// 是否启用调试模式
    pub debug_mode: bool,
}

impl Default for VMConfig {
    fn default() -> Self {
        Self {
            max_stack_size: 1024 * 1024,  // 1M 栈大小
            max_call_depth: 1000,
            enable_stats: true,
            debug_mode: false,
        }
    }
}

impl AquaVM {
    /// 创建新的虚拟机实例
    pub fn new() -> Self {
        Self::with_config(VMConfig::default())
    }
    
    /// 使用指定配置创建虚拟机
    pub fn with_config(config: VMConfig) -> Self {
        let mut vm = Self {
            constants: Vec::new(),
            globals: Vec::new(),
            functions: FxHashMap::default(),
            builtins: FxHashMap::default(),
            instructions: Vec::new(),
            stack: Vec::with_capacity(1024),
            call_stack: Vec::with_capacity(64),
            pc: 0,
            stats: VMStats::default(),
            config,
        };
        
        // 注册内置函数
        vm.register_builtins();
        vm
    }
    
    /// 加载字节码
    pub fn load_bytecode(&mut self, bytecode: &Bytecode) -> Result<()> {
        self.constants = bytecode.constants.clone();
        self.globals = vec![Value::Null; bytecode.global_vars.len()];
        self.functions = bytecode.functions.clone();
        self.instructions = bytecode.instructions.clone();
        
        // 初始化全局变量
        self.initialize_globals(&bytecode.global_vars)?;
        
        Ok(())
    }
    
    /// 运行虚拟机
    pub fn run(&mut self) -> Result<()> {
        self.pc = 0;
        
        while self.pc < self.instructions.len() {
            let instruction = self.instructions[self.pc];
            self.pc += 1;
            
            if self.config.enable_stats {
                self.stats.instructions_executed += 1;
            }
            
            self.execute_instruction(instruction)?;
            
            // 检查栈大小限制
            if self.stack.len() > self.config.max_stack_size {
                return Err(VMError::RuntimeError("Stack overflow".to_string()));
            }
            
            // 更新统计信息
            if self.config.enable_stats {
                self.stats.peak_stack_size = self.stats.peak_stack_size.max(self.stack.len());
                self.stats.peak_call_stack_depth = self.stats.peak_call_stack_depth.max(self.call_stack.len());
            }
        }
        
        Ok(())
    }
    
    /// 执行单条指令 - 高度优化的热路径
    #[inline(always)]
    fn execute_instruction(&mut self, instruction: Instruction) -> Result<()> {
        match instruction.opcode {
            OpCode::LoadConst => {
                let value = self.constants[instruction.operand as usize].clone();
                self.stack.push(value);
            }
            
            OpCode::LoadVar => {
                let value = if self.call_stack.is_empty() {
                    self.globals[instruction.operand as usize].clone()
                } else {
                    let frame = self.call_stack.last().unwrap();
                    frame.locals[instruction.operand as usize].clone()
                };
                self.stack.push(value);
            }
            
            OpCode::StoreVar => {
                let value = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                if self.call_stack.is_empty() {
                    self.globals[instruction.operand as usize] = value;
                } else {
                    let frame = self.call_stack.last_mut().unwrap();
                    frame.locals[instruction.operand as usize] = value;
                }
            }
            
            OpCode::Add => {
                let b = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                let a = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                self.stack.push(a.add(&b)?);
            }
            
            OpCode::Sub => {
                let b = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                let a = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                self.stack.push(a.sub(&b)?);
            }
            
            OpCode::Mul => {
                let b = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                let a = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                self.stack.push(a.mul(&b)?);
            }
            
            OpCode::Div => {
                let b = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                let a = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                self.stack.push(a.div(&b)?);
            }
            
            OpCode::Call => {
                self.handle_call(instruction.operand as usize)?;
            }
            
            OpCode::Return => {
                self.handle_return()?;
            }
            
            OpCode::LoadFunc => {
                let func_name = match &self.constants[instruction.operand as usize] {
                    Value::String(name) => name.clone(),
                    _ => return Err(VMError::TypeError("Expected string for function name".to_string())),
                };
                self.stack.push(Value::String(func_name));
            }
            
            OpCode::Jump => {
                self.pc = instruction.operand as usize;
            }
            
            OpCode::JumpIfTrue => {
                let condition = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                if condition.is_truthy() {
                    self.pc = instruction.operand as usize;
                }
            }
            
            OpCode::JumpIfFalse => {
                let condition = self.stack.pop().ok_or(VMError::StackUnderflow)?;
                if !condition.is_truthy() {
                    self.pc = instruction.operand as usize;
                }
            }
            
            OpCode::TypeCheck => {
                // 暂时跳过类型检查
            }
            
            OpCode::Halt => {
                return Ok(());
            }
            
            _ => {
                return Err(VMError::InvalidOpcode(instruction.opcode as u8));
            }
        }
        
        Ok(())
    }
    
    /// 处理函数调用
    fn handle_call(&mut self, argc: usize) -> Result<()> {
        // 检查调用栈深度
        if self.call_stack.len() >= self.config.max_call_depth {
            return Err(VMError::RuntimeError("Call stack overflow".to_string()));
        }
        
        // 获取参数
        let mut args = Vec::with_capacity(argc);
        for _ in 0..argc {
            args.push(self.stack.pop().ok_or(VMError::StackUnderflow)?);
        }
        args.reverse();
        
        // 获取函数
        let func_name = match self.stack.pop().ok_or(VMError::StackUnderflow)? {
            Value::String(name) => name,
            _ => return Err(VMError::TypeError("Expected function name".to_string())),
        };
        
        if self.config.enable_stats {
            self.stats.function_calls += 1;
        }
        
        // 检查是否为内置函数
        if let Some(builtin) = self.builtins.get(&func_name) {
            let result = builtin.call(&args)?;
            self.stack.push(result);
            return Ok(());
        }
        
        // 检查用户定义函数
        if let Some(function) = self.functions.get(&func_name).cloned() {
            if args.len() != function.parameters.len() {
                return Err(VMError::RuntimeError(
                    format!("Function '{}' expects {} arguments, got {}", 
                           func_name, function.parameters.len(), args.len())
                ));
            }
            
            // 创建新的调用帧
            let mut locals = vec![Value::Null; function.local_vars.len()];
            for (i, arg) in args.into_iter().enumerate() {
                locals[i] = arg;
            }
            
            let frame = CallFrame {
                function,
                return_address: self.pc,
                pc: 0,
                locals,
            };
            
            self.call_stack.push(frame);
            return Ok(());
        }
        
        Err(VMError::FunctionNotFound(func_name))
    }
    
    /// 处理函数返回
    fn handle_return(&mut self) -> Result<()> {
        let return_value = self.stack.pop().ok_or(VMError::StackUnderflow)?;
        
        if let Some(frame) = self.call_stack.pop() {
            self.pc = frame.return_address;
        }
        
        self.stack.push(return_value);
        Ok(())
    }
    
    /// 初始化全局变量
    fn initialize_globals(&mut self, global_vars: &HashMap<String, usize>) -> Result<()> {
        // 这里需要执行全局变量的初始化代码
        // 暂时设置为默认值
        for (_, &index) in global_vars {
            if index < self.globals.len() {
                self.globals[index] = Value::Null;
            }
        }
        Ok(())
    }
    
    /// 注册内置函数
    fn register_builtins(&mut self) {
        self.builtins.insert("print".to_string(), BuiltinFunction::Print);
        self.builtins.insert("str".to_string(), BuiltinFunction::Str);
        self.builtins.insert("int".to_string(), BuiltinFunction::Int);
        self.builtins.insert("float".to_string(), BuiltinFunction::Float);
        self.builtins.insert("len".to_string(), BuiltinFunction::Len);
    }
    
    /// 获取性能统计
    pub fn get_stats(&self) -> &VMStats {
        &self.stats
    }
    
    /// 重置虚拟机状态
    pub fn reset(&mut self) {
        self.stack.clear();
        self.call_stack.clear();
        self.pc = 0;
        self.stats = VMStats::default();
    }
}

impl Default for AquaVM {
    fn default() -> Self {
        Self::new()
    }
}