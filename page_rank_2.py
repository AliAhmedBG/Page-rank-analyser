"""
This page contains code which creates a graph data structure using dictionaries and it contains two algorithms, one being random walk and the other being random distribution
"""
import sys
import os
import time
import argparse
import random

"imported external library networkx"
import networkx as nx

"this function is what initialises and creates the graph data structure"
def load_graph(args):
    """Load graph from text file
    Parameters:
    args -- arguments named tuple
    Returns:
    A networkx directed graph
    """
    "Initialize a directed graph using NetworkX"
    graph = nx.DiGraph()

    "Iterate through the file line by line"
    for line in args.datafile:
        "Splits each line in the file into two urls"
        node, target = line.split()
        "Adds the second URL onto the first as an outgoing edge"
        graph.add_edge(node, target)
    return graph

"this function returns the stats for the graph which are the number of nodes and the number of edges"
def print_stats(graph):
    """Print the number of nodes and edges in the given graph"""
    print("The number of nodes is", graph.number_of_nodes())
    print("The number of edges is", graph.number_of_edges())


def stochastic_page_rank(graph, args):
    """Stochastic PageRank estimation
    Parameters:
    graph -- a graph object as returned by load_graph()
    args -- arguments named tuple
    Returns:
    A dict that assigns each page its hit frequency
    This function estimates the Page Rank by counting how frequently
    a random walk that starts on a random node will after n_steps end
    on each node of the given graph.
    """

    "creates a list of all the nodes in the graph"
    nodes = list(graph.nodes())

    "initialises a dictionary to store the number of hits for each link and sets it to 0"
    hit_count = {node: 0 for node in graph.nodes()}

    "randomly chooses a node to start on"
    current_node = random.choice(nodes)

    "increments the hit_count for the current node by 1"
    hit_count[current_node] += 1

    "carries out the random walk a number of times specified by the argument"
    for x in range(args.repeats):
        "if the current node is not in the graph or has no outgoing edged then choose a new one"
        if current_node not in graph or len(list(graph.out_edges(current_node))) == 0:
            current_node = random.choice(nodes)
        else:
            current_node = random.choice(
                list(graph.neighbors(current_node)))

        "increments the hit counter for the new node"
        hit_count[current_node] += 1

    "returns the hit count dictionary which represents the pagerank estimation"
    return hit_count


def distribution_page_rank(graph, args):
    """Probabilistic PageRank estimation
    Parameters:
    graph -- a graph object as returned by load_graph()
    args -- arguments named tuple
    Returns:
    A dict that assigns each page its probability to be reached
    This function estimates the Page Rank by iteratively calculating
    the probability that a random walker is currently on any node.
    """

    "variable which holds the total number of nodes in the graph"
    nodes = len(graph.nodes())

    "initialises a dictionary to store the probability of each node being hit which at start is set to 1 / each node in the graph"
    node_prob = {node: 1 / nodes for node in graph.nodes()}

    "performs the probability distribution for the specified number of steps by the argument"
    for x in range(args.steps):
        "creates a new dictionary to store the probability of the next node which is set to 0 at the start"
        next_prob = {node: 0 for node in graph.nodes()}

        "loops depending on the number of nodes in the graph"
        for node in graph.nodes():
            "divide the current nodes probability between the neighboring nodes equally"
            p = node_prob[node] / len(graph[node])
            "add this probability to each neighboring node"
            for target in graph[node]:
                next_prob[target] += p

        "update the node probability for he next iteration"
        node_prob = next_prob

    return node_prob

"Create an argument parser to handle command-line input for the PageRank estimation"
parser = argparse.ArgumentParser(description="Estimates page ranks from link information")
parser.add_argument('datafile', nargs='?', type=argparse.FileType('r'),
default=sys.stdin,
help="Textfile of links among web pages as URL tuples")
parser.add_argument('-m', '--method', choices=('stochastic', 'distribution'),
default='stochastic',
help="selected page rank algorithm")
parser.add_argument('-r', '--repeats', type=int, default=1_000_000, help="number of repetitions")
parser.add_argument('-s', '--steps', type=int, default=100, help="number of steps a walker takes")
parser.add_argument('-n', '--number', type=int, default=20, help="number of results shown")

if __name__ == '__main__':
    "parses command line arguments and calls the appropriate method"
    args = parser.parse_args()
    algorithm = distribution_page_rank if args.method == 'distribution' else stochastic_page_rank

graph = load_graph(args)

print_stats(graph)

start = time.time()
ranking = algorithm(graph, args)
stop = time.time()
time = stop - start

"sort nodes by descending page rang value"
top = sorted(ranking.items(), key=lambda item: item[1], reverse=True)
"display top ranked links"
sys.stderr.write(f"Top {args.number} pages:\n")
print('\n'.join(f'{100*v:.2f}\t{k}' for k,v in top[:args.number]))
sys.stderr.write(f"Calculation took {time:.2f} seconds.\n")
