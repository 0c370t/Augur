#!/usr/bin/python2.7

## This module does not interface with the Flask app, but instead helps generate JSON documentation with the CLI

endpoint = {}
outfile = open("outfile.json","rw+")
while True:
    print "+++ New Documentation +++"
    # Get Method Type
    while True:
        method_raw = raw_input("POST or GET: P/G ")
        if method_raw.upper() == 'G':
            endpoint['method'] = "GET"
            break
        elif method_raw.upper() == 'P':
            endpoint['method'] = "POST"
            break
        else:
            print "Invalid input, please enter P/G"

    # Get Basic Fields
    endpoint['title'] = raw_input("Title: ")
    endpoint['route'] = raw_input("Route: ")
    endpoint['description'] = raw_input("Description: ")

    # Get Parameters
    endpoint['parameters'] = {}
    while True:
        param_check = raw_input("Enter a parameter: Y/N ")
        if param_check.upper() == 'N':
            break
        print "++ New Parameter ++"
        new_param = {}
        new_param['field'] = raw_input("Field: ")
        new_param['desc'] = raw_input("Description: ")
        new_param['format'] = raw_input("Format: ")
        endpoint['parameters'][new_param['field']] = new_param

    # Get Examples
    endpoint['examples'] = []
    while True:
        example_check = raw_input("Enter an example: Y/N ")
        if example_check.upper() == 'N':
            break
        print "++ New Example ++"
        new_example = {}
        new_example['desc'] = raw_input("Example Description: ")
        new_example['args'] = raw_input("GET Parameters: ")
        new_example['form'] = raw_input("Form inputs: ")
        endpoint['examples'] += [new_example]

    # Print it all out
    print '\n\n+++++++++++++++++++++++++++++++++++++++++++'
    if endpoint['method'] == "POST":
        endpoint['response'] = "Image File as Response"
    else:
        endpoint['response'] = ""
        print "Ensure the response is field is filled in before you commit this!"
    out = ""
    out += '\n\t{'
    out += '\n\t\t"%s":"%s",' % ('method', endpoint['method'])
    out += '\n\t\t"%s":"%s",' % ('title', endpoint['title'])
    out += '\n\t\t"%s":"%s",' % ('route', endpoint['route'])
    out += '\n\t\t"%s":"%s",' % ('description', endpoint['description'])

    out += '\n\t\t"%s": {' % ('parameters')
    if 'parameters' in endpoint:
        for param in endpoint['parameters']:
            out += '\n\t\t\t"%s":{' % param
            out += '\n\t\t\t\t"%s":"%s",' % ('field',endpoint['parameters'][param]['field'])
            out += '\n\t\t\t\t"%s":"%s",' % ('desc',endpoint['parameters'][param]['desc'])
            out += '\n\t\t\t\t"%s":"%s"' % ('format',endpoint['parameters'][param]['format'])
            out += '\n\t\t\t},'
        out = out[:-1]
        out += '\n\t\t},'
    if 'examples' in endpoint:
        out += '\n\t\t"example_requests":['
        for example in endpoint['examples']:
            out += '\n\t\t\t{'
            out += '\n\t\t\t\t"%s":"%s",' % ('desc', example['desc'])
            out += '\n\t\t\t\t"%s":"%s",' % ('args', example['args'])
            out += '\n\t\t\t\t"%s":"%s"' % ('form', example['form'])
            out += '\n\t\t\t},'
        out = out[:-1]
        out += '\n\t\t],'
    out += '\n\t\t"response":"%s"' % endpoint['response']
    out += '\n\t}'
    print out
    outfile.write(out+",\n")
    print '+++++++++++++++++++++++++++++++++++++++++++'

    loop_check = raw_input("Create another endpoint documentation: Y/N ")
    if loop_check.upper() != 'Y':
        break
