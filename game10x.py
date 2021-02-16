import getch
import copy
import random
import os
import sys


def getChunkData(map, pos):
    temp = []
    for line in map[(pos[0] // 10, pos[1] // 10)]:
        temp.append(" ".join(line))
    return temp  # Returns the lines of a chunk


def getCompleteMapString(map, pos):
    mapArray = []
    chunkData = []

    # Grabs all chunkdata around player
    chunkData.extend(getChunkData(map, (pos["x"] - 10, pos["y"] - 10)))  # Top
    chunkData.extend(getChunkData(map, (pos["x"], pos["y"] - 10)))
    chunkData.extend(getChunkData(map, (pos["x"] + 10, pos["y"] - 10)))

    chunkData.extend(getChunkData(map, (pos["x"] - 10, pos["y"])))  # Middle
    chunkData.extend(getChunkData(map, (pos["x"], pos["y"])))
    chunkData.extend(getChunkData(map, (pos["x"] + 10, pos["y"])))

    chunkData.extend(getChunkData(map, (pos["x"] - 10, pos["y"] + 10)))  # Bottom
    chunkData.extend(getChunkData(map, (pos["x"], pos["y"] + 10)))
    chunkData.extend(getChunkData(map, (pos["x"] + 10, pos["y"] + 10)))
    #

    for i in range(10):
        mapArray.append(
            chunkData[i] + " " + chunkData[i + 10] + " " + chunkData[i + 20]
        )  # Top
    for i in range(10):
        mapArray.append(
            chunkData[i + 30] + " " + chunkData[i + 40] + " " + chunkData[i + 50]
        )  # Middle
    for i in range(10):
        mapArray.append(
            chunkData[i + 60] + " " + chunkData[i + 70] + " " + chunkData[i + 80]
        )  # Bottom

    return mapArray


class bcolors:  # Not quite sure how this works, colors can be used by adding these to strings
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def getUIStrings():
    strings = [
        "W: UP",
        "A: LEFT",
        "S: DOWN",
        "D: RIGHT",
        "E: Place block",
        "R: Place shop",
        " ",
        "Pos: {}".format((pos["x"], pos["y"])),
        "Money: {}".format(money),
        "Blocks: {}".format(inv["block"]),
        "Shops: {}".format(inv["shop"]),
    ]
    if inv["block"]:
        strings[4] = bcolors.OKGREEN + strings[4] + bcolors.ENDC
    else:
        strings[4] = bcolors.FAIL + strings[4] + bcolors.ENDC

    if inv["shop"]:
        strings[5] = bcolors.OKGREEN + strings[5] + bcolors.ENDC
    else:
        strings[5] = bcolors.FAIL + strings[5] + bcolors.ENDC

    if canWalk(pos, "w"):
        strings[0] = bcolors.OKGREEN + strings[0] + bcolors.ENDC
    else:
        strings[0] = bcolors.FAIL + strings[0] + bcolors.ENDC

    if canWalk(pos, "a"):
        strings[1] = bcolors.OKGREEN + strings[1] + bcolors.ENDC
    else:
        strings[1] = bcolors.FAIL + strings[1] + bcolors.ENDC

    if canWalk(pos, "s"):
        strings[2] = bcolors.OKGREEN + strings[2] + bcolors.ENDC
    else:
        strings[2] = bcolors.FAIL + strings[2] + bcolors.ENDC

    if canWalk(pos, "d"):
        strings[3] = bcolors.OKGREEN + strings[3] + bcolors.ENDC
    else:
        strings[3] = bcolors.FAIL + strings[3] + bcolors.ENDC
    return strings


def printMap(map, pos):

    prevBlock = getBlock(
        pos["x"], pos["y"]
    )  # Remembers where the player is, else blocks might be deleted
    map[(pos["x"] // 10, pos["y"] // 10)][pos["y"] % 10][
        pos["x"] % 10
    ] = "@"  # Sets the player position to @

    mapString = getCompleteMapString(map, pos)
    croppedString = ""

    drawing = False
    for i, line in enumerate(mapString):
        if i + 10 < len(mapString):
            if "@" in mapString[i + 10]:
                drawing = True
        if i - 10 >= 0:
            if "@" in mapString[i - 10]:
                drawing = False
        if drawing:
            croppedString += line + "\n"

    croppedString = croppedString.splitlines()
    for line in croppedString:
        if "@" in line:
            xPos = line.find("@")
            break

    print("/" + "~" * 42 + "\\")
    strings = getUIStrings()
    strings.extend([""] * 100)
    for i, line in enumerate(croppedString):
        print("| {} | {}".format(line[xPos - 20 : xPos + 20], strings[i]))
    print("\\" + "~" * 42 + "/")

    map[(pos["x"] // 10, pos["y"] // 10)][pos["y"] % 10][
        pos["x"] % 10
    ] = prevBlock  # Sets the block back to the original blcok


def getBlock(x, y):
    return map[(x // 10, y // 10)][y % 10][x % 10]  # Find the block on the map


def setBlock(x, y, value):
    map[(x // 10, y // 10)][y % 10][x % 10] = value  # Set the block on the map


def placeBlock(pos):
    if inv["block"]:
        setBlock(pos["x"], pos["y"], "#")
        inv["block"] -= 1


def canWalk(pos, key):
    tempPos = copy.deepcopy(pos)
    placeTurn = False
    if key == "r":
        return True
    elif key == "e":
        return True
    elif key == "w":
        tempPos["y"] -= 1
    elif key == "s":
        tempPos["y"] += 1
    elif key == "a":
        tempPos["x"] -= 1
    elif key == "d":
        tempPos["x"] += 1

    global money  # Money doesn't exist here, bring it
    if not placeTurn:
        block = getBlock(tempPos["x"], tempPos["y"])
        if block == "O":
            return False
        if block == "#":
            if deleteMode:
                return True
            elif money == 0:
                return False
            else:
                if (
                    getBlock(
                        tempPos["x"] + (tempPos["x"] - pos["x"]),
                        tempPos["y"] + (tempPos["y"] - pos["y"]),
                    )
                    == "█"
                ):
                    return False
                if (
                    getBlock(
                        tempPos["x"] + (tempPos["x"] - pos["x"]),
                        tempPos["y"] + (tempPos["y"] - pos["y"]),
                    )
                    == "#"
                ):
                    return True
                else:
                    return True
        if block == "█":
            if deleteMode:
                return True
            else:
                return False

        elif block == "$":
            return True  # Return new position

        elif block == "*":
            tempPos["x"] = random.randint(
                abs(tempPos["x"] * 3) * -1, abs(tempPos["x"] * 3)
            )  # Generates a range, limited by current distence to not make it limited
            tempPos["y"] = random.randint(
                abs(tempPos["y"] * 3) * -1, abs(tempPos["y"] * 3)
            )
            generateChunk(tempPos)
            setBlock(tempPos["x"], tempPos["y"], " ")
            return tempPos

    return tempPos  # Empty position, return the new position


def placeShop():
    global pos
    if inv["shop"]:
        setBlock(pos["x"], pos["y"], "%")
        inv["shop"] -= 1
    pass


def trap():
    os.system("clear")
    print("You have died.")
    print("Press any key to end")
    getch.getch()
    exit()


def shop(pos, tempPos):
    if shopMenu(tempPos):
        setBlock(tempPos["x"], tempPos["y"], " ")
        return tempPos
    else:
        return pos


def weakWall(tempPos, pos, deleteMode):
    global money
    if deleteMode:
        setBlock(tempPos["x"], tempPos["y"], " ")
        return tempPos
    elif money == 0:
        return pos
    else:
        if (
            getBlock(
                tempPos["x"] + (tempPos["x"] - pos["x"]),
                tempPos["y"] + (tempPos["y"] - pos["y"]),
            )
            == "█"
        ):
            return pos
        if (
            getBlock(
                tempPos["x"] + (tempPos["x"] - pos["x"]),
                tempPos["y"] + (tempPos["y"] - pos["y"]),
            )
            == "#"
        ):
            setBlock(tempPos["x"], tempPos["y"], " ")
            setBlock(
                tempPos["x"] + (tempPos["x"] - pos["x"]),
                tempPos["y"] + (tempPos["y"] - pos["y"]),
                "█",
            )
            return tempPos
        else:
            setBlock(
                tempPos["x"] + (tempPos["x"] - pos["x"]),
                tempPos["y"] + (tempPos["y"] - pos["y"]),
                "#",
            )
            setBlock(tempPos["x"], tempPos["y"], " ")
            money -= 1
            return tempPos


def teleport(tempPos):
    tempPos["x"] = random.randint(
        abs(tempPos["x"] * 3) * -1, abs(tempPos["x"] * 3)
    )  # Generates a range, limited by current distence to not make it infinite
    tempPos["y"] = random.randint(abs(tempPos["y"] * 3) * -1, abs(tempPos["y"] * 3))
    generateChunk(tempPos)
    setBlock(tempPos["x"], tempPos["y"], " ")
    return tempPos


def move(pos):
    tempPos = copy.deepcopy(
        pos
    )  # Don't want to actually move the character, use a copy of the position
    key = getch.getch().lower()
    placeTurn = False
    if key == "r":
        placeTurn = True
        placeShop()
    elif key == "e":
        placeTurn = True
        placeBlock(pos)
    elif key == "w":
        tempPos["y"] -= 1
    elif key == "s":
        tempPos["y"] += 1
    elif key == "a":
        tempPos["x"] -= 1
    elif key == "d":
        tempPos["x"] += 1

    global money  # Money doesn't exist here, bring it
    if placeTurn:
        return pos
    else:
        block = getBlock(tempPos["x"], tempPos["y"])

        if block == "X":
            trap()

        elif block == "O":
            money += 1
            return pos

        elif block == "%":
            return shop(pos, tempPos)

        if block == "#":
            return weakWall(tempPos, pos, deleteMode)
        if block == "█":
            if deleteMode:
                setBlock(tempPos["x"], tempPos["y"], " ")
                return tempPos
            else:
                return pos

        elif block == "$":
            setBlock(tempPos["x"], tempPos["y"], " ")  # Delete money
            money += 1  # Increase money
            return tempPos  # Return new position

        elif block == "*":
            teleport(tempPos)

        return tempPos  # Empty position, return the new position


def shopMenu(pos):  # Called when a shop is interacted with
    global deleteMode
    global money
    print("(1) move mode ($0)")
    print("(2) delete mode ($10)")
    print("(3) infinite block ($25)")
    print("(4) block ($1)")
    print("(5) shop ($10)")
    choice = getch.getch()
    if choice == "1":
        deleteMode = False
        return True
    elif choice == "2":
        if money >= 10:
            money -= 10
            deleteMode = True
        return True
    elif choice == "3":
        if money >= 25:
            money -= 25
            setBlock(pos["x"], pos["y"], "O")
        return False
    elif choice == "4":
        if money >= 1:
            inv["block"] += 1
            money -= 1
        return False
    elif choice == "5":
        if money >= 10:
            inv["shop"] += 1
            money -= 10
    else:
        return False


def randChunk():  # This is used for generating
    chunk = []
    temp = []
    for i in range(10):  # Generate 10 lines of characters, this is to fill the map
        for i in range(10):  # Generates 10 characters
            randNum = random.randint(
                0, 100
            )  # If within range, put symbol, used for chance
            if randNum >= 0 and randNum <= 10:
                temp.append("#")
            elif randNum >= 10 and randNum <= 20:
                temp.append("$")
            elif randNum >= 20 and randNum <= 25:
                temp.append("X")
            elif randNum == 99:
                temp.append("%")
            elif randNum == 100:
                temp.append("*")
            else:
                temp.append(" ")
        chunk.append(temp)  # Returns the line of data generated
        temp = []
    return chunk


def generateChunk(pos):
    if (
        pos["x"] // 10,
        pos["y"] // 10,
    ) not in map:  # if chunk doesn't already exist, generate one
        map[(pos["x"] // 10, pos["y"] // 10)] = randChunk()


def generateSurrondingChunks():  # Generate all chunks around player
    generateChunk({"x": pos["x"], "y": pos["y"] + 10})  # Up
    generateChunk({"x": pos["x"], "y": pos["y"] - 10})  # Down
    generateChunk({"x": pos["x"] + 10, "y": pos["y"]})  # Left
    generateChunk({"x": pos["x"] - 10, "y": pos["y"]})  # Right

    generateChunk({"x": pos["x"] - 10, "y": pos["y"] + 10})  # Up and Right
    generateChunk({"x": pos["x"] + 10, "y": pos["y"] + 10})  # Up and Left
    generateChunk({"x": pos["x"] - 10, "y": pos["y"] - 10})  # Down and Right
    generateChunk({"x": pos["x"] + 10, "y": pos["y"] - 10})  # Down and Left


os.system("clear")
print("Zander's infinite world!")
print("W: UP")
print("A: LEFT")
print("S: DOWN")
print("D: RIGHT")
print("E: Place block")
print("R: Place shop")
print()
getch.getch()
os.system("clear")

map = {}  # Creates the empty map, this is where chunks will be stored.
pos = {"x": 0, "y": 0}
money = 0
deleteMode = False
generateChunk({"x": pos["x"], "y": pos["y"]})  # Generate the chunk the player is on
setBlock(pos["x"], pos["y"], " ")  # Makes sure the player doesn't spawn on something
inv = {"block": 0, "shop": 0}  # Sets default inventory
while True:
    generateSurrondingChunks()  # Generates the chunks around the player
    print()
    printMap(map, pos)  # Prints the map
    pos = move(pos)  # Gets position of player
    os.system("clear")  # Clears the screen

