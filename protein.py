"""DNA to protein.

Goal: Reach a model for DNA expression of a cell.
    DNA is made of codons.
    Transcription/Translation profile masks genes in DNA.
    Gene combinations create codons.
    codons transcribe,translate into proteins.

Protein performs functions via reactions:
    - signalling
    - structure
    - movement
    - ionization

Proteins bind to a ligand based on a unique "shape"
Proteins have "handles" that bind it somewhere in the "cell"
Large proteins can have several "domains"

https://www.ncbi.nlm.nih.gov/books/NBK26911/

> Molecules in the cell encounter each other very frequently
> because of their continual random thermal movements.

> Eventually, any population of antibody molecules and ligands
> will reach a steady state, or equilibrium, in which
> the number of binding (association) events per second is precisely
> equal to the number of “unbinding” (dissociation) events

> Actin binds to actin to form filaments.

> Enzymes bind to ligands (substrates)
> Enzymes speed up reactions, often by a factor of a million or more
> Products of enzymes become substrates for other enzymes

> The result is an elaborate network of metabolic pathways that provides
> the cell with energy and generates the many large and small molecules
> that the cell needs

> Reaction rate increases like a log function.

> Thus, the signal receptor protein rhodopsin, which is made by the
> photoreceptor cells in the retina, detects light by means of a small
> molecule, retinal, embedded in the protein (Figure 3-53A).
> Retinal changes its shape when it absorbs a photon of light, and this
> change causes the protein to trigger a cascade of enzymatic reactions that
> eventually leads to an electrical signal being carried to the brain.

> The efficiency of enzymes in accelerating chemical reactions is crucial
> to the maintenance of life. Cells, in effect, must race against the
> unavoidable processes of decay, which—if left unattended—cause
> macromolecules to run downhill toward greater and greater disorder.
> If the rates of desirable reactions were not greater than the rates
> of competing side reactions, a cell would soon die.

> Reaction rates can be increased without raising substrate concentrations
> by bringing the various enzymes involved in a reaction sequence together
> to form a large protein assembly known as a multienzyme complex
> (Figure 3-54). Because this allows the product of enzyme A to be passed
> directly to enzyme B, and so on, diffusion rates need not be limiting,
> even when the concentrations of the substrates in the cell as a whole are
> very low. It is perhaps not surprising, therefore, that such
> enzyme complexes are very common, and they are involved in nearly all
> aspects of metabolism—including the central genetic processes of
> DNA, RNA, and protein synthesis. In fact, few enzymes in eucaryotic
> cells may be left to diffuse freely in solution; instead, most
> seem to have evolved binding sites that concentrate them with
> other proteins of related function in particular regions of the cell,
> thereby increasing the rate and efficiency of the
> reactions that they catalyze.

Increased concentration == increased reaction
> membranes can segregate particular substrates and the enzymes
> that act on them into the same membrane-enclosed compartment, such as the
> endoplasmic reticulum or the cell nucleus. If, for example, a compartment
> occupies a total of 10% of the volume of the cell, the concentration of
> reactants in the compartment may be increased as much as 10 times
> compared with the same cell with no compartmentalization.

Overproduction ~= regulation
Proteins and nodes in protein pathways can be inhibited by overproduction
as the substrate feeds back to the previous parents' regulatory sites

Linkage affects positive or negative regulation
Proteins with multiple sites are changed at each binding.
Binding in one place affects the affinity for binding in the other.

activity = 90%
inhibition *= 100
activity = 10%

Signal proteins turn on and off based on particular presence of ligands.
Ie. a condition causes them to be on/off and transmit something.
Note: Destruction of signal cells causes cascading reactions!

Some proteins act like "ON if x and y and z else OFF"

Some proteins act like "ON while I am phosphorylated else OFF"

Proteins regulate traffic to different compartments

Small proteins can latch/unlatch to activate large ones.
(small condition -> large reaction)

Motor proteins can contract, swim, crawl
Ex. "walking protein" along an actin filament
    using "magnet boots" kind of locomotion (bind/unbind feet)
Thermodynamics say that it is reversible (random)
but due to input energy and reactions (atp->adp) it becomes
directed in a certain way.

Ion pump:
    trans-membrane protein has:
        atp receptor (for phosphorylation)
        ion receptor
    steps:
        ion binds to helix
        phosphorylation happens (energy)
        protein bends
        ion is released (to other membrane)
        phosphor is released

DNA replication/etc is done by large protein assemblies.
"protein machines"

Proteins cannot be used alone to model behavior - must also
consider the environment, non-fatty acid molecules, etc...

Cell cycle control
    DNA synthesis
    amino acid metabolism
    protein degradation
    cell polarity
    mating repsonse
    signalling
    protein modification
Chroma(tin/some) structure
    mating
    rna processing
    rna splicing
    dna repair
    recombination
    DNA synthesis
    mitosis
    protein modification
RNA polymerase II transcription
    carb metabolism
    transcription
    RNA splicing
    signalling
    mating
    protein modification
More:
    recombination
    dna repair
    vesicular transport
    membrane function
    cell structure
        protein folding
            protein translocation
                fatty acid/sterol metabolism
                nuclear cytoplasmic transport
---

Model proteins as small structures.
Proteins tend to react with neiboring molecules/proteins
via specific filtering profiles.
Each reaction changes the state of the protein
which affects the filtering profile of other sites.


sites a(0,1), b(0,1)
nodes closed(0), opening(1), open(2) closing(3)
edges 0 -(a1b1)-> 1 -> 2 -(a1b0)-> 3 -> 0
"""
