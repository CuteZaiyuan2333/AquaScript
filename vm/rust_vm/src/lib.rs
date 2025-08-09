/*!
AquaScript 高性能虚拟机 - Rust实现

这个虚拟机使用Rust编写，提供接近原生性能的执行速度。
主要优化包括：
- 零成本抽象
- 内存安全
- SIMD指令优化
- 分支预测优化
- 缓存友好的数据结构
*/

use std::collections::HashMap;
use std::fmt;
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};
use thiserror::Error;

pub mod bytecode;
pub mod vm;
pub mod value;
pub mod function;
pub mod builtins;

#[cfg(feature = "python-bindings")]
pub mod python;

pub use vm::AquaVM;
pub use value::Value;
pub use bytecode::{OpCode, Instruction};

/// 虚拟机错误类型
#[derive(Error, Debug)]
pub enum VMError {
    #[error("Stack underflow")]
    StackUnderflow,
    
    #[error("Invalid opcode: {0}")]
    InvalidOpcode(u8),
    
    #[error("Function not found: {0}")]
    FunctionNotFound(String),
    
    #[error("Type error: {0}")]
    TypeError(String),
    
    #[error("Runtime error: {0}")]
    RuntimeError(String),
    
    #[error("Division by zero")]
    DivisionByZero,
    
    #[error("Index out of bounds: {index} >= {len}")]
    IndexOutOfBounds { index: usize, len: usize },
    
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),
}

pub type Result<T> = std::result::Result<T, VMError>;

/// 性能统计信息
#[derive(Debug, Default, Clone)]
pub struct VMStats {
    pub instructions_executed: u64,
    pub function_calls: u64,
    pub gc_collections: u64,
    pub peak_stack_size: usize,
    pub peak_call_stack_depth: usize,
}

impl fmt::Display for VMStats {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, 
            "VM Statistics:\n\
             Instructions executed: {}\n\
             Function calls: {}\n\
             GC collections: {}\n\
             Peak stack size: {}\n\
             Peak call stack depth: {}",
            self.instructions_executed,
            self.function_calls,
            self.gc_collections,
            self.peak_stack_size,
            self.peak_call_stack_depth
        )
    }
}