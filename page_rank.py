"""
This script estimates the PageRank of a graph of URLs.

It provides two algorithms:
1. Stochastic PageRank (random walk)
2. Distribution PageRank (probabilistic distribution)

It can be run from the command line and will display the top-ranked pages.
"""

import sys
import os
import time
import argparse
import random
# Allows for usage of the progress bar
from progress import Progress


def load_graph(args):
    """
    Load a graph from a text file.

    Each line in the file contains two URLs: 'node target'.
    This creates a dictionary where each node maps to a list of its target URLs.

    Parameters:
    - args: arguments from the command line, including the datafile

    Returns:
    - graph (dict): A mapping of {node: [target1, target2, ...]}
    """
    graph = {}
    for line in args.datafile:
        # Split line into node and target
        node, target = line.split()
        if node in graph:
            # Add target to existing node
            graph[node].append(target)
        else:
            # Create new entry for node
            graph[node] = [target]
    return graph


def print_stats(graph):
    """
    Print simple statistics about the graph:
    - Number of nodes
    - Number of edges

    Parameters:
    - graph (dict): The graph loaded from the data file
    """
    print("The number of nodes is ", len(graph))
    edge_count = 0
    for node, child in graph.items():
        edge_count += len(child)
    print("The number of edges is ", edge_count)


def stochastic_page_rank(graph, args):
    """
    Stochastic PageRank estimation (random walk approach).

    The algorithm:
    - Start at a random node
    - Walk randomly through the graph for a number of steps
    - Count how often each node is visited
    - The frequency approximates its PageRank score

    Parameters:
    - graph (dict): The graph as returned by load_graph()
    - args: Command-line arguments (contains number of repeats, etc.)

    Returns:
    - hit_count (dict): Mapping of {node: visit_count}
    """

    # List of all nodes
    nodes = list(graph.keys())

    # Initialize hit counter for each node
    hit_count = {node: 0 for node in graph}

    # Start on a random node
    current_node = random.choice(nodes)
    hit_count[current_node] += 1

    # Set up progress bar for long runs
    prog = Progress(args.repeats, title="Stochastic PageRank")

    # Perform the random walk for 'args.repeats' steps
    for x in range(args.repeats):
        # If node has no outgoing edges, jump to a random node
        if current_node not in graph or len(graph[current_node]) == 0:
            current_node = random.choice(nodes)
        else:
            # Otherwise, move to a random outgoing edge
            current_node = random.choice(graph[current_node])

        # Increment hit count for the node landed on
        hit_count[current_node] += 1

        # Update the progress bar periodically
        prog += 1
        # Show every 10k steps to avoid slowing down
        if x % 10000 == 0:
            prog.show()

    # Finish the progress bar when done
    prog.finish()

    return hit_count


def distribution_page_rank(graph, args):
    """
    Distribution PageRank estimation (probabilistic approach).

    The algorithm:
    - Start with an equal probability of being at each node
    - Iteratively distribute probability mass over outgoing edges
    - After a number of steps, the probabilities converge to PageRank

    Parameters:
    - graph (dict): The graph as returned by load_graph()
    - args: Command-line arguments (contains number of steps, etc.)

    Returns:
    - node_prob (dict): Mapping of {node: probability}
    """
    nodes = len(graph.keys())

    # Initially, every node has equal probability
    node_prob = {node: 1 / nodes for node in graph}

    # Iterate for 'args.steps' steps
    for x in range(args.steps):
        next_prob = {node: 0 for node in graph}
        for node in graph:
            # Only distribute if node has outgoing edges
            if len(graph[node]) > 0:
                p = node_prob[node] / len(graph[node])
                for target in graph[node]:
                    next_prob[target] += p
        node_prob = next_prob

    return node_prob


# Set up command-line argument parser
parser = argparse.ArgumentParser(description="Estimates page ranks from link information")
parser.add_argument('datafile', nargs='?', type=argparse.FileType('r'),
                    default=sys.stdin,
                    help="Textfile of links among web pages as URL tuples")
parser.add_argument('-m', '--method', choices=('stochastic', 'distribution'),
                    default='stochastic',
                    help="Selected PageRank algorithm")
parser.add_argument('-r', '--repeats', type=int, default=1_000_000,
                    help="Number of repetitions for stochastic method")
parser.add_argument('-s', '--steps', type=int, default=100,
                    help="Number of steps for distribution method")
parser.add_argument('-n', '--number', type=int, default=20,
                    help="Number of top results to show")


if __name__ == '__main__':
    # Parse the command-line arguments
    args = parser.parse_args()

    # Choose the algorithm based on the user input
    algorithm = distribution_page_rank if args.method == 'distribution' else stochastic_page_rank

    # Load the graph and print stats
    graph = load_graph(args)
    print_stats(graph)

    # Run the selected algorithm
    start = time.time()
    ranking = algorithm(graph, args)
    stop = time.time()
    elapsed = stop - start

    # Sort nodes by their rank (highest first)
    top = sorted(ranking.items(), key=lambda item: item[1], reverse=True)

    # Output top ranked pages
    sys.stderr.write(f"Top {args.number} pages:\n")
    print('\n'.join(f'{100*v:.2f}\t{k}' for k, v in top[:args.number]))
    sys.stderr.write(f"Calculation took {elapsed:.2f} seconds.\n")
