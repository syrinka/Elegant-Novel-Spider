import click
from rich.markdown import Markdown

import os

from ens.paths import TOPIC
from ens.console import echo
from ens.exceptions import TopicNotFound


def get_topics():
    topics = []
    for file in os.listdir(TOPIC):
        name, ext = os.path.splitext(file)
        if ext != '.md':
            continue
        else:
            topics.append(name)
    return topics


@click.command('topic')
@click.argument('topic', required = False)
def main(topic):
    if not topic:
        echo('Usage: ens topic [TOPIC]\n')
        echo('Available topics:')
        for topic in get_topics():
            echo(f'  [green]{topic}')
                
    else:
        path = os.path.join(TOPIC, topic + '.md')
        if not os.path.exists(path):
            raise TopicNotFound(topic)

        md = open(path, encoding='utf-8').read()
        echo(Markdown(md))

