import argparse

"""
Main function
"""
def main():
    """
    parse user input
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify the config.json in other place", default="config.json")

    args = parser.parse_args()
    print(args.config)

if __name__ == "__main__":
    main()

