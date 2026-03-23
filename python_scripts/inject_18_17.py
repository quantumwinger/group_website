from bs4 import BeautifulSoup

with open("publications.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

abs_18 = "The reactivity of water, a fundamental process in aqueous chemistry, is profoundly altered under nanoconfinement. The properties of the confining material determine the layer dependence of autoionization, dictating whether reactions are stabilized at the interface or in the subsurface. In weakly interacting walls (Wall A), hydroxide is destabilized at the interface and the reaction proceeds preferentially in the subsurface, whereas in strongly interacting walls (Wall B) the interfacial and subsurface states are nearly isoenergetic, reducing selectivity. This contrast arises from confinement-enforced coordination motifs where hydronium remains tri-coordinated across environments, while hydroxide is restricted to tetra coordination at the interface but adopts hypercoordinated states in the subsurface. Mechanical flexibility of the confining framework further modulates the overall thermodynamics by reducing the entropic penalty, as water molecules can explore a broader configurational space compared to rigid pores. These findings establish how layer-specific solvation and wall flexibility govern confined-water reactivity, providing molecular-level design principles for engineering dynamic nanoscale interfaces in catalysis, energy storage, and molecular separations."

abs_17 = "Rising energy demands underscore the need for renewable energy solutions such as solar energy. Covalent organic frameworks (COFs), with their tunable compositions, structures, and photophysical properties, are promising candidates; however, a comprehensive understanding of their composition-structure–property relationships remains limited. Here, combining all-electron quantum chemistry with coarse-grained Holstein Hamiltonians, we show that although slipped-stacked configurations are generally most stable, the degree of slipping is strongly influenced by the nature of the functional groups and does not follow simple electron-donating or -withdrawing trends. While van der Waals interactions primarily drive the stacking behavior, electrostatic contributions unique to each substituent modulate its extent. Furthermore, we find that in highly symmetric lattice backbones, small substituent changes have minimal effect on electronic structure, whereas symmetry-breaking functionalization offers a robust and effective route to tune electronic, transport, and photophysical properties. While the stacking arrangement primarily governs interlayer electron coherence, its influence diminishes in the high-disorder regime. Our findings provide fundamental insights and design principles to guide the development of high-performance COFs for photocatalytic applications."

for pub_item in soup.find_all(class_='pub-item'):
    num_div = pub_item.find(class_='pub-number')
    if not num_div: continue
    num = num_div.get_text(strip=True)
    
    if num == "18":
        tt = pub_item.find(class_='pub-abstract-tooltip')
        if not tt:
            tt = soup.new_tag('div', attrs={'class': 'pub-abstract-tooltip'})
            pub_item.append(tt)
        tt.string = abs_18
    elif num == "17":
        tt = pub_item.find(class_='pub-abstract-tooltip')
        if not tt:
            tt = soup.new_tag('div', attrs={'class': 'pub-abstract-tooltip'})
            pub_item.append(tt)
        tt.string = abs_17

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Injected perfectly!")
