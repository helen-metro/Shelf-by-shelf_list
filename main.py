import os
import argparse
import preprocessing


def main():
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--dateFolder", required=True, help="Date Folder Data Input")
    parser.add_argument("--branchCode", required=True, type=int, 
                        default=32, help="Branch Code for filtering")

    args = parser.parse_args()

    preprocessing.run_splitting_process(args.branchCode, 
                                        args.dateFolder)



if __name__ == "__main__":
    main()