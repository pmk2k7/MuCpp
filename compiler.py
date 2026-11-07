import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class Diagnostic:
    file: str
    line: int
    column: int
    severity: str  # 'error', 'fatal error', 'warning', 'note'
    message: str
    raw: str

@dataclass
class CompilationResult:
    success: bool
    return_code: int
    command: List[str]
    stdout: str
    stderr: str
    diagnostics: List[Diagnostic]
    output_path: Optional[str] = None
    duration_sec: float = 0.0

class CompilerManager:
    """Manages C/C++ compiler detection, flags, compiling, and error parsing."""
    
    DEFAULT_DEVCPP_GCC = r"C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe"
    DEFAULT_DEVCPP_C = r"C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\gcc.exe"

    def __init__(self):
        self.cxx_compiler = self.detect_compiler("g++", self.DEFAULT_DEVCPP_GCC)
        self.c_compiler = self.detect_compiler("gcc", self.DEFAULT_DEVCPP_C)
        self.standard = self.detect_default_standard(self.cxx_compiler)
        self.optimization = "-O2"
        self.warnings = ["-Wall", "-Wextra"]
        self.custom_flags: List[str] = []
        self.linker_flags: List[str] = []
        self.include_dirs: List[str] = []
        self.lib_dirs: List[str] = []
        self.run_in_external_console = True

    @classmethod
    def detect_default_standard(cls, cxx_path: str) -> str:
        """Determines best supported standard flag for the detected compiler."""
        try:
            if not os.path.isfile(cxx_path) and shutil.which(cxx_path) is None:
                return "-std=c++11"
            res = subprocess.run([cxx_path, "-dumpversion"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
            ver_str = res.stdout.strip().split('.')[0]
            if ver_str.isdigit():
                major = int(ver_str)
                if major >= 7:
                    return "-std=c++17"
                elif major >= 5:
                    return "-std=c++14"
        except Exception:
            pass
        return "-std=c++11"

    @classmethod
    def detect_compiler(cls, binary_name: str, fallback_path: str) -> str:
        """Finds compiler binary from system PATH or Dev-Cpp MinGW installation."""
        which_path = shutil.which(binary_name)
        if which_path and os.path.isfile(which_path):
            return which_path
        if os.path.isfile(fallback_path):
            return fallback_path
        
        # Look in standard alternate locations
        candidates = [
            r"C:\MinGW\bin" + f"\\{binary_name}.exe",
            r"C:\msys64\mingw64\bin" + f"\\{binary_name}.exe",
            r"C:\msys64\ucrt64\bin" + f"\\{binary_name}.exe",
            r"C:\TDM-GCC-64\bin" + f"\\{binary_name}.exe"
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return binary_name

    def is_available(self, is_cxx: bool = True) -> bool:
        comp = self.cxx_compiler if is_cxx else self.c_compiler
        return os.path.isfile(comp) or shutil.which(comp) is not None

    def build_command(self, source_files: List[str], output_executable: str, is_cxx: bool = True) -> List[str]:
        compiler = self.cxx_compiler if is_cxx else self.c_compiler
        cmd = [compiler]
        if is_cxx and self.standard:
            cmd.append(self.standard)
        if self.optimization:
            cmd.append(self.optimization)
        cmd.extend(self.warnings)
        for inc in self.include_dirs:
            if inc.strip():
                cmd.append(f"-I{inc.strip()}")
        for flag in self.custom_flags:
            if flag.strip():
                cmd.append(flag.strip())
        
        cmd.extend(source_files)
        cmd.extend(["-o", output_executable])
        
        for lib in self.lib_dirs:
            if lib.strip():
                cmd.append(f"-L{lib.strip()}")
        for lflag in self.linker_flags:
            if lflag.strip():
                cmd.append(lflag.strip())
        return cmd

    def parse_diagnostics(self, text: str) -> List[Diagnostic]:
        """
        Parses GCC/Clang error and warning messages.
        Format:
        filename:line:col: severity: message
        or
        filename:line: severity: message
        """
        diagnostics = []
        pattern = re.compile(
            r'^(?P<file>[a-zA-Z]:[\\/][^:\r\n]+|[^:\r\n]+):(?P<line>\d+):(?:(?P<col>\d+):)?\s*(?P<severity>fatal error|error|warning|note):\s*(?P<msg>.+)$',
            re.IGNORECASE | re.MULTILINE
        )
        for line in text.splitlines():
            clean_line = line.strip()
            match = pattern.match(clean_line)
            if match:
                file_path = match.group("file").strip()
                line_no = int(match.group("line"))
                col_no = int(match.group("col")) if match.group("col") else 1
                severity = match.group("severity").lower().strip()
                msg = match.group("msg").strip()
                diagnostics.append(Diagnostic(
                    file=file_path,
                    line=line_no,
                    column=col_no,
                    severity=severity,
                    message=msg,
                    raw=clean_line
                ))
        return diagnostics

    def compile(self, source_files: List[str], output_executable: str, is_cxx: bool = True) -> CompilationResult:
        start_time = time.time()
        cmd = self.build_command(source_files, output_executable, is_cxx)
        
        try:
            # Hide child window on Windows during compilation
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags,
                encoding='utf-8',
                errors='replace'
            )
            duration = time.time() - start_time
            stdout_str = proc.stdout or ""
            stderr_str = proc.stderr or ""
            all_output = stdout_str + "\n" + stderr_str
            diagnostics = self.parse_diagnostics(all_output)
            success = (proc.returncode == 0) and os.path.isfile(output_executable)
            
            return CompilationResult(
                success=success,
                return_code=proc.returncode,
                command=cmd,
                stdout=stdout_str,
                stderr=stderr_str,
                diagnostics=diagnostics,
                output_path=output_executable if success else None,
                duration_sec=duration
            )
        except Exception as ex:
            return CompilationResult(
                success=False,
                return_code=-1,
                command=cmd,
                stdout="",
                stderr=str(ex),
                diagnostics=[],
                duration_sec=time.time() - start_time
            )

    def run_executable(self, executable_path: str, working_dir: Optional[str] = None) -> Optional[subprocess.Popen]:
        """Runs the compiled binary in an external console window with pause on completion, just like Dev-C++."""
        if not os.path.isfile(executable_path):
            return None
        
        if not working_dir:
            working_dir = os.path.dirname(executable_path)
            
        if self.run_in_external_console and os.name == 'nt':
            # Classic Dev-C++ behavior: spawn cmd.exe that executes the program, prints newline, and pauses
            quoted_exe = f'"{executable_path}"'
            cmd = f'cmd.exe /c "{quoted_exe} & echo. & echo -------------------------------- & echo Process exited. Press any key to continue . . . & pause >nul"'
            proc = subprocess.Popen(
                cmd,
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return proc
        else:
            # Internal execution
            proc = subprocess.Popen(
                [executable_path],
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return proc
