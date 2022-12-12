def classFactory(iface):
    # Load the RevealAddressPlugin class from the RevealAddressPlugin.py file
    from .RevealAddressPlugin import RevealAddressPlugin
    return RevealAddressPlugin(iface)