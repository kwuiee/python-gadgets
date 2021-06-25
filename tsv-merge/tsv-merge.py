#!/usr/bin/env python
# noqa: D100
import csv
from collections import OrderedDict

import click


@click.command()
@click.option("-o", "--output", type=click.Path(writable=True), required=True)
@click.option(
    "-i", "--input", help="Input file containing files to merge.", type=click.Path(readable=True), required=True
)
def cli(output, input):
    final = OrderedDict()
    with open(input) as fp:
        for i in fp:
            each = open(i.strip())
            header = map(lambda x: x.strip(), each.readline().strip("\n").split("\t"))
            for j in header:
                final[j] = 0
            each.close()

    output = open(output, "w")
    writer = csv.DictWriter(output, delimiter="\t", fieldnames=final.keys())
    writer.writeheader()
    with open(input) as fp:
        for i in fp:
            each = open(i.strip())
            reader = csv.DictReader(each, delimiter="\t")
            for j in reader:
                writer.writerow(j)
            each.close()
    output.close()
    return


if __name__ == "__main__":
    cli()
