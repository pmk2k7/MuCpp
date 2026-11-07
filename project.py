import json
import os
from dataclasses import asdict, dataclass, field
from typing import List, Optional

TEMPLATES = {
    "Console Application (C++)": {
        "ext": ".cpp",
        "type": "console",
        "code": """#include <iostream>

int main(int argc, char** argv) {
    std::cout << "Hello, Dev-Cpp!" << std::endl;
    return 0;
}
"""
    },
    "Console Application (C)": {
        "ext": ".c",
        "type": "console",
        "code": """#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    printf("Hello, Dev-Cpp in C!\\n");
    return 0;
}
"""
    },
    "Windows GUI Application": {
        "ext": ".cpp",
        "type": "windows",
        "code": """#include <windows.h>

/* This is where all the input to the window goes to */
LRESULT CALLBACK WndProc(HWND hwnd, UINT Message, WPARAM wParam, LPARAM lParam) {
    switch(Message) {
        case WM_DESTROY: {
            PostQuitMessage(0);
            break;
        }
        default:
            return DefWindowProc(hwnd, Message, wParam, lParam);
    }
    return 0;
}

/* The 'main' function of Win32 GUI programs: this is where execution starts */
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    WNDCLASSEX wc;
    HWND hwnd;
    MSG msg;

    memset(&wc,0,sizeof(wc));
    wc.cbSize        = sizeof(WNDCLASSEX);
    wc.lpfnWndProc   = WndProc;
    wc.hInstance     = hInstance;
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
    wc.lpszClassName = "MuCppWindowClass";
    wc.hIcon         = LoadIcon(NULL, IDI_APPLICATION);
    wc.hIconSm       = LoadIcon(NULL, IDI_APPLICATION);

    if(!RegisterClassEx(&wc)) {
        MessageBox(NULL, "Window Registration Failed!", "Error!", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    hwnd = CreateWindowEx(WS_EX_CLIENTEDGE, "MuCppWindowClass", "MuCpp Application",
        WS_VISIBLE | WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 640, 480, NULL, NULL, hInstance, NULL);

    if(hwnd == NULL) {
        MessageBox(NULL, "Window Creation Failed!", "Error!", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    while(GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return msg.wParam;
}
"""
    },
    "Dynamic Link Library (DLL)": {
        "ext": ".cpp",
        "type": "dll",
        "code": """#include <windows.h>

#define DLL_EXPORT __declspec(dllexport)

extern "C" DLL_EXPORT int AddNumbers(int a, int b) {
    return a + b;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            break;
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}
"""
    },
    "Empty Project": {
        "ext": ".cpp",
        "type": "console",
        "code": ""
    }
}


@dataclass
class Project:
    name: str
    project_file_path: str
    source_files: List[str] = field(default_factory=list)
    project_type: str = "console"  # 'console', 'windows', 'dll', 'static_lib'
    compiler_flags: List[str] = field(default_factory=list)
    linker_flags: List[str] = field(default_factory=list)

    @property
    def project_dir(self) -> str:
        return os.path.dirname(self.project_file_path)

    @property
    def output_executable(self) -> str:
        ext = ".dll" if self.project_type == "dll" else (".a" if self.project_type == "static_lib" else ".exe")
        return os.path.join(self.project_dir, f"{self.name}{ext}")

    def save(self):
        data = {
            "name": self.name,
            "project_type": self.project_type,
            "source_files": [os.path.relpath(f, self.project_dir) for f in self.source_files],
            "compiler_flags": self.compiler_flags,
            "linker_flags": self.linker_flags
        }
        with open(self.project_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load(cls, file_path: str) -> 'Project':
        project_dir = os.path.dirname(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        abs_files = [os.path.normpath(os.path.join(project_dir, f)) for f in data.get("source_files", [])]
        return cls(
            name=data.get("name", "Project"),
            project_file_path=file_path,
            source_files=abs_files,
            project_type=data.get("project_type", "console"),
            compiler_flags=data.get("compiler_flags", []),
            linker_flags=data.get("linker_flags", [])
        )

    @classmethod
    def create_new(cls, project_dir: str, project_name: str, template_name: str) -> 'Project':
        os.makedirs(project_dir, exist_ok=True)
        template = TEMPLATES.get(template_name, TEMPLATES["Console Application (C++)"])
        
        project_file = os.path.join(project_dir, f"{project_name}.mcpp")
        main_filename = f"main{template['ext']}"
        main_path = os.path.join(project_dir, main_filename)
        
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(template["code"])
            
        proj = cls(
            name=project_name,
            project_file_path=project_file,
            source_files=[main_path],
            project_type=template["type"]
        )
        if template["type"] == "windows":
            proj.linker_flags.append("-mwindows")
            
        proj.save()
        return proj
