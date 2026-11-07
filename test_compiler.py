import os
from compiler import CompilerManager

def run_test():
    cm = CompilerManager()
    print("CXX Compiler:", cm.cxx_compiler)
    print("Is available:", cm.is_available(True))

    test_cpp = "test_hello.cpp"
    with open(test_cpp, "w", encoding="utf-8") as f:
        f.write("#include <iostream>\nint main() {\n    std::cout << \"Dev-Cpp Recreation Test!\" << std::endl;\n    return 0;\n}\n")

    res = cm.compile([test_cpp], "test_hello.exe", is_cxx=True)
    print("Compile Success:", res.success)
    print(f"Duration: {res.duration_sec:.2f}s")
    print("Output Path:", res.output_path)
    print("Diagnostics count:", len(res.diagnostics))

    # Error parsing test
    test_err = "test_error.cpp"
    with open(test_err, "w", encoding="utf-8") as f:
        f.write("#include <iostream>\nint main() {\n    undeclared_var = 10;\n    return 0;\n}\n")

    err_res = cm.compile([test_err], "test_error.exe", is_cxx=True)
    print("Error compile success (expected False):", err_res.success)
    print("Error count detected:", len(err_res.diagnostics))
    for d in err_res.diagnostics:
        print(f" -> {d.file}:{d.line}:{d.column} [{d.severity}] {d.message}")

    for f in ["test_hello.cpp", "test_hello.exe", "test_error.cpp"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    run_test()
