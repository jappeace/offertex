def userChoice(msg, options):
    print(msg)
    optmap = {}
    for n,line in enumerate(options):
        optmap[n] = line
        print("%d: %s" % (n,str(line).rstrip()))
    try:
        selected = int(input("Uw keuze: \n"))
    except ValueError:
        print("Ongeldige invoer, ik acepteer alleen maar integers")
        return userChoice(msg, options)
    if selected in optmap:
        return optmap[selected]
    else:
        print("%d is niet beschikbaar als keuze" % selected)
        return userChoice(msg, options)

