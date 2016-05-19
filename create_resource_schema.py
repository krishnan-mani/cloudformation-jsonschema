#!/usr/bin/env python

import tools
import resource_properties
import val
import tweak_resource_schema

import requests
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache


def main(argv):
    sess = CacheControl(requests.Session(),
                        cache=FileCache('.web_cache'))
    requests.get = sess.get

    resource_schema = tools.load('resource-stage1.json')
    # resource has a type
    val.val({"Type": "Something"}, resource_schema)

    resource_type_names = tools.get_all_resource_type_names()
    tools.update_all_resource_patterns_by_name(
        resource_schema,
        resource_type_names
    )
    # all resource types are known
    val.val({"Type": "AWS::Lambda::Function"}, resource_schema)

    for resource_type_name in resource_type_names:
        print >> sys.stderr, resource_type_name
        resource_properties.set_resource_properties(resource_schema, resource_type_name)

    # simple resource properties are validated
    val.val(
        {
            "Type": "AWS::IAM::User",
            "Properties": {
                "Groups": ["some_group"]
            }
        },
        resource_schema,
        '#/definitions/resource_types/AWS::IAM::User'
    )
    del resource_schema['definitions']['resource_template']

    all_properties = resource_properties.all_res_properties()
    resource_schema['definitions']['property_types'] = all_properties

    tweak_resource_schema.fix_RecordSetGroup(resource_schema)
    tweak_resource_schema.add_Custom(resource_schema)
    tweak_resource_schema.add_CreationPolicy(resource_schema)
    tweak_resource_schema.add_UpdatePolicy(resource_schema)

    if len(argv) == 2 and argv[1].endswith('json'):
        tools.write(resource_schema, argv[1])
    else:
        print tools.print_(resource_schema)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))