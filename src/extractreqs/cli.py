import argparse
from .extractreqs import extract_requirements

def main():
    parser = argparse.ArgumentParser(
        description="Extract requirements.txt from a Python source directory"
    )
    parser.add_argument("src", help="Path to source directory")
    parser.add_argument("-o", "--output", default="requirements.txt",
                        help="Output requirements file (default: requirements.txt)")
    
    args = parser.parse_args()
    reqs = extract_requirements(args.src, False)
    
    with open(args.output, "w") as f:
        f.write("\n".join(reqs))
    
    print(f"[+] Extracted {len(reqs)} requirements -> {args.output}")
