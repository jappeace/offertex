def userChoice(msg, options):
    print(msg)
    optmap = {}
    for n,line in enumerate(options):
        optmap[n] = line
        print("%d: %s" % (n,str(line).rstrip()))
    try:
        selected = int(input("your choice: \n"))
    except ValueError:
        print("invalid input try again")
        return userChoice(msg, options)
    if selected in optmap:
        return optmap[selected]
    else:
        print("%d is not available as choice" % selected)
        return userChoice(msg, options)

