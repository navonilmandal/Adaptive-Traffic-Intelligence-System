import os

def generate_network():
    print("Generating large 6x6 SUMO network...")
    command = (
        "netgenerate --grid "
        "--grid.x-number 6 --grid.y-number 6 " # Increased to 6x6
        "--grid.length 150 "
        "--default.lanenumber 2 "
        "--output-file network.net.xml"
    )
    os.system(command)
    print("network.net.xml generated successfully! City size increased.")

if __name__ == "__main__":
    generate_network()