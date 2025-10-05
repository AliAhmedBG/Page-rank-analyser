"""
This script estimates the PageRank of nodes in a web graph using two methods:
1. Stochastic (random walk)
2. Distribution (probability redistribution)

This version uses the NetworkX library to build and manage the graph.
"""

import sys
import os
import time
import argparse
import random
# External graph library for easier graph management
import networkx as nx
# Custom progress bar for visual feedback
from progress import Progress


def load_graph(args):
    """
    Load graph from a text file.

    Each line in the file should contain two URLs (from, to),
    representing a directed edge in the graph.

    Parameters:
    - args: Parsed command-line arguments

    Returns:
    - A NetworkX directed graph
    """
    # Directed graph
    graph = nx.DiGraph()

    for line in args.datafile:
        node, target = line.split()
        # Add edge from node to target
        graph.add_edge(node, target)

    return graph


def print_stats(graph):
    """
    Print basic graph statistics:
    - Total number of nodes
    - Total number of directed edges
    """
    print("The number of nodes is", graph.number_of_nodes())
    print("The number of edges is", graph.number_of_edges())


def stochastic_page_rank(graph, args):
    """
    Estimate PageRank using the stochastic (random walk) method.

    Method:
    - Start at a random node
    - Move randomly from node to node based on edges
    - Count visits to estimate PageRank

    Parameters:
    - graph: NetworkX DiGraph
    - args: Command-line arguments

    Returns:
    - Dictionary of {node: hit_count}
    """

    nodes = list(graph.nodes())
    # Hit count for each node
    hit_count = {node: 0 for node in graph.nodes()}

    current_node = random.choice(nodes)
    hit_count[current_node] += 1

    prog = Progress(args.repeats, title="Stochastic PageRank")

    for x in range(args.repeats):
        # If the node has no outgoing edges, move to random node
        if current_node not in graph or len(list(graph.out_edges(current_node))) == 0:
            current_node = random.choice(nodes)
        else:
            # Move to one of the neighboring nodes randomly
            current_node = random.choice(list(graph.neighbors(current_node)))

        hit_count[current_node] += 1

        prog += 1
        # periodically show progress bar to now slow program down
        if x % 10000 == 0:
            prog.show()

    prog.finish()
    return hit_count


def distribution_page_rank(graph, args):
    """
    Estimate PageRank using the distribution (iterative) method.

    Method:
    - Start with equal probability on all nodes
    - At each step, redistribute the probabilities to outgoing edges
    - After several iterations, the values converge to PageRank

    Parameters:
    - graph: NetworkX DiGraph
    - args: Command-line arguments

    Returns:
    - Dictionary of {node: probability}
    """
    nodes = len(graph.nodes())
    # Equal initial probability
    node_prob = {node: 1 / nodes for node in graph.nodes()}

    for _ in range(args.steps):
        # Reset probability for each iteration
        next_prob = {node: 0 for node in graph.nodes()}

        for node in graph.nodes():
            # Distribute current probability to each outgoing edge
            if len(graph[node]) > 0:
                p = node_prob[node] / len(graph[node])
                for target in graph[node]:
                    next_prob[target] += p

        # Update for next iteration
        node_prob = next_prob

    return node_prob


# Argument parser for command-line usage
parser = argparse.ArgumentParser(description="Estimates page ranks from link information")

parser.add_argument('datafile', nargs='?', type=argparse.FileType('r'),
                    default=sys.stdin,
                    help="Text file of links among web pages as URL tuples (from to)")

parser.add_argument('-m', '--method', choices=('stochastic', 'distribution'),
                    default='stochastic',
                    help="Choose the PageRank algorithm to use")

parser.add_argument('-r', '--repeats', type=int, default=1_000_000,
                    help="Number of steps for stochastic PageRank")

parser.add_argument('-s', '--steps', type=int, default=100,
                    help="Number of iterations for distribution PageRank")

parser.add_argument('-n', '--number', type=int, default=20,
                    help="How many top results to display")


if __name__ == '__main__':
    # Parse command-line arguments
    args = parser.parse_args()

    # Choose algorithm
    algorithm = distribution_page_rank if args.method == 'distribution' else stochastic_page_rank

    # Load the graph and print statistics
    graph = load_graph(args)
    print_stats(graph)

    # Execute the selected PageRank algorithm
    start = time.time()
    ranking = algorithm(graph, args)
    stop = time.time()
    elapsed = stop - start

    # Sort results by score, highest first
    top = sorted(ranking.items(), key=lambda item: item[1], reverse=True)

    # Print top results
    sys.stderr.write(f"Top {args.number} pages:\n")
    print('\n'.join(f'{100 * v:.2f}\t{k}' for k, v in top[:args.number]))
    sys.stderr.write(f"Calculation took {elapsed:.2f} seconds.\n")
