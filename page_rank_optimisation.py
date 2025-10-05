"""
This script estimates the PageRank of nodes in a web graph using two methods:
1. Stochastic (random walk)
2. Distribution (probability redistribution)

This version is optimized compared to page_rank.py:
- Uses defaultdict for faster graph construction
- Precomputes outgoing edge counts to reduce repeated calculations
"""

import sys
import os
import time
import argparse
import random
# Efficient dictionary subclass for lists
from collections import defaultdict
# Custom progress bar for feedback
from progress import Progress


def load_graph(args):
    """
    Load graph from a text file.

    Each line in the file should contain two URLs (from, to),
    representing a directed edge in the graph.

    Parameters:
    - args: Parsed command-line arguments

    Returns:
    - A defaultdict mapping a URL (str) to a list of target URLs (str)
    """
    # Automatically initializes empty lists
    graph = defaultdict(list)

    for line in args.datafile:
        node, target = line.split()
        # Append target to node’s adjacency list
        graph[node].append(target)

    return graph


def print_stats(graph):
    """
    Print basic graph statistics:
    - Total number of nodes
    - Total number of directed edges
    """
    print("The number of nodes is", len(graph))

    edge_count = 0
    for node, child in graph.items():
        edge_count += len(child)

    print("The number of edges is", edge_count)


def stochastic_page_rank(graph, args):
    """
    Estimate PageRank using the stochastic (random walk) method.

    Optimisation:
    - Precompute the number of outgoing edges for each node
    - Use defaultdict for hit counts

    Parameters:
    - graph: Dictionary of node → [outgoing nodes]
    - args: Command-line arguments

    Returns:
    - Dictionary of {node: hit_count}
    """
    # precalculate number of outgoing edges
    out_node = {node: len(targets) for node, targets in graph.items()}

    nodes = list(graph.keys())
    # Default to 0 hits for all nodes
    hit_count = defaultdict(int)

    current_node = random.choice(nodes)
    hit_count[current_node] += 1

    prog = Progress(args.repeats, title="Stochastic PageRank")

    for x in range(args.repeats):
        # If the node has no outgoing edges, move to random node
        if current_node not in graph or out_node[current_node] == 0:
            current_node = random.choice(nodes)
        else:
            # Choose one of the outgoing edges at random
            current_node = random.choice(graph[current_node])

        hit_count[current_node] += 1

        prog += 1
        # Show progress bar periodically
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
    - graph: Dictionary of node → [outgoing nodes]
    - args: Command-line arguments

    Returns:
    - Dictionary of {node: probability}
    """
    nodes = len(graph.keys())
    # Equal initial probability
    node_prob = {node: 1 / nodes for node in graph}

    for x in range(args.steps):
        next_prob = {node: 0 for node in graph}

        for node in graph:
            if len(graph[node]) > 0:
                # Divide current node’s probability equally among neighbors
                p = node_prob[node] / len(graph[node])
                for target in graph[node]:
                    next_prob[target] += p

        # Update for next iteration
        node_prob = next_prob

    return node_prob


# Command-line argument parser
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
