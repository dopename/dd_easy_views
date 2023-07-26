from django.template.loader_tags import BlockNode
from django.template.base import Lexer, Parser
from django.template.loader import get_template

def combine_templates(base_template, content_template, block_name=None):
    """
    Takes two templates and combines them into one.
    """
    base_template = get_template(base_template)
    content_template = get_template(content_template)
    base_blocks = base_template.template.nodelist.get_nodes_by_type(BlockNode)
    base_block = None

    for block in base_blocks:
        if block_name and block.name == block_name or ((not block_name) and 'content' in block.name):
            base_block = block
            break
    
    if not base_block:
        raise Exception('No content block found in base template.')
    
    content_block = content_template.template.nodelist
    base_block.nodelist = content_block
    return base_template