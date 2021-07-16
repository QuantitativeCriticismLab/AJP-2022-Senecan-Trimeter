import re
import json
from glob import glob
import matplotlib.pyplot as plt

def load_data():
    """
    Load all the data into one huge dictionary (with the first key being the
    play's name)
    :return:
    """
    plays = glob("data/fullScansions/*.json")
    plays = [x.split("/")[-1].split(".")[0] for x in plays]
    data = {}
    for play in plays:
        with open("data/fullScansions/" + play + ".json") as file:
            data[play] = {"scansion": json.load(file)}
        with open("data/antilabe/" + play + ".txt") as file:
            data[play]["antilabe"] = file.readlines()
    return data

def make_elision_graph(data):
    """
    Create a graph that compares the plays by elision frequency and save that
    graph to a file so that it can then be inserted into README.md
    :param data:
    :return:
    """
    plays = sorted(list(data.keys()))
    elision = [data[play]["scansion"]["stats"]["global"]
               ["elision"]["frequencies"]["total"] for play in plays]
    figure = plt.figure(figsize=(20, 5))
    plt.bar(plays, elision, color='black')
    plt.xlabel("Play")
    plt.ylabel("Elision rate")
    plt.title("Seneca and Neo-Latin plays by elision rate")
    plt.savefig("reports/figures/elision.png")

def make_antilabe_graph(data):
    """
    Create a graph that shows that resolutions tend to be more frequent in
    antilabe
    :param data:
    :return:
    """
    plays = sorted(list(data.keys()))
    ratios = []
    for i in range(len(plays)):
        play = plays[i]
        meter = data[play]["scansion"]["text"]["0"]["meter"]
        res_total = data[play]["scansion"]["stats"][meter]["resolution"]["counts"]["total"]
        antilabe_res = []  # list that for each antilabe line has a resolution rate
        line_to_resolution = {}
        # create a dictionary of all the lines
        failed = 0
        for line in data[play]["scansion"]["text"].values():
            pattern = re.sub("[^\^_*]", "", line["pattern"])
            res_count = len(pattern) - 12
            key = re.sub("[^a-z]", "", line["scansion"].lower())
            key = re.sub("v", "u", re.sub("j", "i", key))
            line_to_resolution[key] = res_count
            if len(pattern) == 0:
                line_to_resolution[key] = -1
                failed += 1
        # calculate resolution rate in antilabe
        antilabe_failed = 0
        for line in data[play]["antilabe"]:
            key = re.sub("[^a-z]", "", line.lower())
            key = re.sub("v", "u", re.sub("j", "i", key))
            if key not in line_to_resolution.keys():
                print("Cannot find an antilabe line!")
            elif line_to_resolution[key] == -1:
                print("Antilabe line not scanned: " + line)
                antilabe_failed += 1
                antilabe_res.append(0)
            else:
                antilabe_res.append(line_to_resolution.get(key, 0))
        total_lines = len(data[play]["scansion"]["text"].keys()) - failed
        # print(play)
        # print(len(data[play]["scansion"]["text"].keys()))
        # print(len(data[play]["scansion"]["text"].keys()) - failed - len(data[play]["antilabe"]) + antilabe_failed)
        # print(len(data[play]["antilabe"]) - antilabe_failed)
        # print(sum(antilabe_res))
        # print(data[play]["scansion"]["stats"][meter]["resolution"]["counts"]["total"] - sum(antilabe_res))
        antilabe_rate = sum(antilabe_res) / len(antilabe_res)
        no_antilabe_rate = (res_total - sum(antilabe_res)) / (total_lines - len(antilabe_res))
        # print(no_antilabe_rate)
        ratios.append(antilabe_rate/no_antilabe_rate)

    figure = plt.figure(figsize=(20, 5))
    plt.bar(plays, ratios, color='black')
    plt.xlabel("Play")
    plt.ylabel("Ratio of the elision rate in lines with antilabe and without antilabe")
    plt.title("Relationship between antilabe and resolution rate")
    plt.savefig("reports/figures/antilabe.png")

def resolution_table(data):
    """
    Return a string to print the resolution distribution in the README.md file
    :param data:
    :return:
    """
    result = ""
    for play in sorted(list(data.keys())):
        result += "|" + play
        for foot in range(6):
            meter = data[play]["scansion"]["text"]["0"]["meter"]
            result += "|" + str(round(data[play]["scansion"]
                                  ["stats"][meter]["resolution"]
                                  ["frequencies"][str(foot)], 2))
        result += "|\n"
    return result


def elision_table(data):
    """
    Return a string to print the elision distribution in the README.md file
    :param data:
    :return:
    """
    result = ""
    for play in sorted(list(data.keys())):
        result += "|" + play
        for foot in range(6):
            result += "|" + str(round(data[play]["scansion"]
                                  ["stats"]["global"]["elision"]
                                  ["frequencies"][str(foot)], 2))
        result += "|\n"
    return result

def scansion_stats(data):
    """
    Return a string summarizing the scansion process and the number of lines
    left unscanned, etc.
    :param data:
    :return:
    """
    total = 0
    auto = 0
    verified = 0
    corrected = 0
    semi_auto = 0
    manual = 0
    unscanned = 0
    for play in data.keys():
        stats = data[play]["scansion"]["stats"]["global"]["method"]
        auto += stats["automatic"] + stats["automatic (verified)"] + \
                stats["manual (corrected)"]
        verified += stats["automatic (verified)"]
        corrected += stats["manual (corrected)"]
        semi_auto += stats["semi-automatic"]
        manual += stats["manual"]
        if "failed" in stats:
            unscanned += stats["failed"]
        if "failed (many options)" in stats:
            unscanned += stats["failed (many options)"]
        total += sum(stats.values())
    return "Overall, we analyzed %s lines of iambic trimeter, of which %s" \
           " were scanned fully automatically (automatic scansions of most " \
           "difficult lines were verified in %s cases and corrected in %s" \
           " cases), %s were scanned" \
           " with human help (i.e. the human had to select from several" \
           " scansion options), %s had to be scanned manually, and %s lines" \
           " from the Neo-Latin texts were left unscanned due to metrical" \
           " anomalies. These latter %s lines are not included in the" \
           " analysis below." %(total, auto, verified, corrected, semi_auto,
                                manual, unscanned, unscanned)

if __name__ == "__main__":
    data = load_data()
    make_elision_graph(data)  # makes elision figure
    make_antilabe_graph(data)  # makes antilabe figure
    FIGS = {"RESOLUTION_TABLE": resolution_table(data),
            "ELISION_TABLE": elision_table(data),
            "SCANSION_STATS": scansion_stats(data)}
    with open("reports/reportTemplate.md") as file:  # read the template:
        template = file.readlines()
    for i in range(len(template)):  # insert the data into the template text:
        for label in FIGS.keys():
            template[i] = re.sub(r"\$" + label + "\$", FIGS[label], template[i])
    with open("reports/report.md", "w") as file:  # save the result:
        file.writelines(template)
