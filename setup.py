from setuptools import setup, find_namespace_packages

setup(
    name="mcp-server-practices",
    version="0.3.0",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "practices=mcp_server_practices.cli:main",
            "practices-server=mcp_server_practices.mcp_server:main",
            "mcp-server-practices=mcp_server_practices:mcp_server_practices_main",
        ],
    },
)
