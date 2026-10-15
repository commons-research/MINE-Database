# Biosynthetic building blocks for a Pickaxe pathway-reconstruction test (first target: quercetin)

Research note, 2026-10-15. It answers three questions:

1. Which building blocks do natural products (specialised metabolites) come from?
2. Which concrete molecules should go into a Pickaxe starting set?
3. Can this repo rebuild the quercetin route from them?

Claims that were not observed directly in a source, or computed from repo files and runs, are marked **[INFERENCE]**.

**Sources and abbreviations used below**

- **Dewick** = P. M. Dewick, *Medicinal Natural Products: A Biosynthetic Approach*, 3rd ed., Wiley 2009 ([DOI 10.1002/9780470742761](https://doi.org/10.1002/9780470742761)). Chapter 2 and the table of contents were read from the publisher's reading sample ([PDF](https://content.e-bookshelf.de/media/reading/L-578797-150924c91b.pdf)). Page numbers are the printed book pages.
- **KEGG** pages were read through the KEGG REST API (`https://rest.kegg.jp/get/<id>`, `…/link/compound/<map>`).
- **MetaCyc** pages are MetaCyc 30.0 as shown on biocyc.org.
- **SMILES** come from PubChem (`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/<CID>/property/SMILES,InChIKey/CSV`).

## TL;DR

- **Four precursor pathways plus amino acids.** Dewick (p. 8) says: "By far the most important building blocks employed in the biosynthesis of secondary metabolites are derived from the intermediates acetyl coenzyme A (acetyl-CoA), shikimic acid, mevalonic acid, and methylerythritol phosphate". Building blocks based on amino acids are added to these. Phe, Tyr and Trp come from the shikimate pathway. Ornithine and lysine "are important alkaloid precursors".
- **Eight structural building units.** Dewick (pp. 10–11, Fig. 2.2) names these units:
  - C₁: SAM methyl
  - C₂: acetyl-CoA / malonyl-CoA
  - C₅: the isoprene unit (from mevalonate or MEP)
  - C₆C₃: phenylpropyl, from Phe/Tyr. Shortened forms are C₆C₂ and C₆C₁.
  - C₆C₂N: from Phe/Tyr
  - indole.C₂N: from Trp
  - C₄N: from ornithine
  - C₅N: from lysine

  §1 gives each unit with its molecules and SMILES.
- **Quercetin = 1 × C₆C₃ + 3 × C₂.**
  - The C₆C₃ unit comes from p-coumaroyl-CoA (from Phe). It supplies the B ring plus C2, C3 and C4.
  - Three malonyl-CoA supply the C₂ units that build the A ring (KEGG map00941; Dewick Fig. 2.3, where naringin = "C₆C₃ + 3 × C₂ + sugars").
- **The canonical route has 8 enzymatic steps**: PAL → C4H → 4CL → CHS → CHI → F3H → F3′H → FLS. A Pickaxe run from L-Phe therefore needs **at least 8 generations** (`-g 8`). From p-coumaric acid it needs 6; from naringenin it needs 3.
- **Repo finding: the route breaks twice with the MetaCyc generalized rules.** I ran every step for one generation with all 1,216 selectable rules (§4.4).
  - **Reproduced:** PAL, C4H, 4CL, CHI, F3H, F3′H, and F3′H on kaempferol.
  - **Not reproduced:** CHS (p-coumaroyl-CoA → naringenin chalcone) and FLS (dihydroflavonol → flavonol, for both taxifolin and dihydrokaempferol).
  - **Consequence:** a plain run from phenylalanine cannot produce quercetin.
  - **Update:** both gaps now have hand-written rules (`rule_CHS`, `rule_FLS`) in `mine_database/data/metacyc_rules/metacyc_custom_rules.tsv`; see §4.2 points 6–7.
- **Malonyl-CoA does not fix CHS.**
  - Malonyl-CoA is not a coreactant in either repo coreactant list.
  - No generalized rule maps the MetaCyc CHS reaction.
  - Pickaxe's "full" operators fill every `Any` reactant slot with the same molecule (`mine_database/reactions.py:32-34, 277-279`). A p-coumaroyl-CoA + 3 malonyl-CoA condensation therefore cannot be formed from two different pool compounds.
  - Adding malonyl-CoA to the starting set is harmless for correctness but does not enable CHS.
  - **Update:** `MALONYL-COA` is now a coreactant in `metacyc_coreactants.tsv`, and a hand-written CHS rule (`rule_CHS`) lives in `mine_database/data/metacyc_rules/metacyc_custom_rules.tsv`; see §4.2 point 6.
- **All 44 SMILES in this note were validated with RDKit 2024.03.6 in the repo environment.** Each one parsed, and its recomputed InChIKey matched PubChem's (44/44). Both CSV blocks were also loaded through `Pickaxe.load_compound_set` / `load_targets` (16 + 1 compounds and 1 target loaded).

## 1. Structural building units (Dewick ch. 2, Fig. 2.2)

Dewick (p. 10): "Relatively few building blocks are routinely employed … The structural features of these building blocks are shown in Figure 2.2." After listing them (p. 11): "These eight building blocks will form the basis of many of the natural product structures discussed in the following chapters."

| Unit | Fragment it contributes (Dewick pp. 10–11) | Biosynthetic origin | Molecule(s) for a Pickaxe start set (PubChem CID) | Example natural products (Dewick Fig. 2.3, p. 12) |
|---|---|---|---|---|
| **C₁** | "a single carbon atom, usually in the form of a methyl group … attached to oxygen or nitrogen, but occasionally to carbon or sulfur". The methylenedioxy group (–OCH₂O–) is also a C₁ unit. | "derived from the *S*-methyl of L-methionine", via *S*-adenosylmethionine (SAM; p. 12, Fig. 2.4) | SAM (34755). **Already a coreactant** (`METHYL_DONOR_CoF`), so leave it out. L-Met (6137) is optional. | podophyllotoxin (… + 4 × C₁), papaverine (… + 4 × C₁), cocaine (… + 2 × C₁), lysergic acid (… + C₁) |
| **C₂** | An acetyl group, a long alkyl chain (fatty acids), or part of an aromatic ring (phenols). For the chain and ring cases, "acetyl-CoA is first converted into the more reactive malonyl-CoA before its incorporation" (p. 10). | Acetate pathway: acetyl-CoA, from pyruvate or β-oxidation (p. 8) | malonyl-CoA (644066), the chain extender. acetyl-CoA (444493) is **already a coreactant** (`ACETYL-COA`). | orsellinic acid (4 × C₂), tetrahydrocannabinolic acid (6 × C₂ + 2 × C₅), naringin (C₆C₃ + 3 × C₂ + sugars) |
| **C₅** | The branched "isoprene" unit (p. 10–11) | Mevalonate is made from 3 × acetyl-CoA, and only 5 of its 6 carbons are used. MEP is made from pyruvate + glyceraldehyde 3-P via deoxyxylulose phosphate (p. 11). Both lead to IPP and DMAPP ([KEGG map00900 description](https://rest.kegg.jp/get/map00900)). | IPP (1195). (R)-mevalonic acid (439230) and MEP (443198) to exercise the upstream steps. DMAPP (647) is **already a coreactant** (`PRENYL_DONOR_CoF`). | parthenolide (3 × C₅), lysergic acid (+ C₅), THCA (+ 2 × C₅) |
| **C₆C₃** | A phenylpropyl unit. The C₃ side chain may be saturated, unsaturated or oxygenated (p. 11). | L-Phe or L-Tyr, with "loss of the amino group" (p. 11). In KEGG, Phe → cinnamic acid by deamination, then hydroxylation to coumaric acid ([map00940 description](https://rest.kegg.jp/get/map00940)). | L-Phe (6140), L-Tyr (6057). Direct entry points: trans-cinnamic acid (444539), p-coumaric acid (637542). | naringin (C₆C₃ + 3 × C₂ + sugars), podophyllotoxin (2 × C₆C₃ + 4 × C₁) |
| **C₆C₂, C₆C₁** | "modified shortened forms of the C₆C₃ system", formed when the side chain is cleaved (p. 11) | From C₆C₃ by side-chain cleavage (p. 11). Benzoic acids from C₆C₃ are covered in Dewick ch. 4, p. 157 (table of contents). | **[INFERENCE: representative molecules, not named by Dewick in ch. 2]**: phenylacetic acid (999) for C₆C₂; benzoic acid (243) and 4-hydroxybenzoic acid (135) for C₆C₁ | cocaine (… + (C₆C₁) …), papaverine (C₆C₂N + (C₆C₂) + 4 × C₁) |
| **C₆C₂N** | Phe/Tyr skeleton without the carboxyl carbon. "L-tyrosine being by far the more common precursor" (p. 11). | L-Phe / L-Tyr, decarboxylated | L-Tyr (6057), L-Phe (6140). Tyramine (5610) and dopamine (681) are the decarboxylated forms; both are in [KEGG map01063](https://rest.kegg.jp/link/compound/map01063) (checked). | papaverine (C₆C₂N + …). Dewick ch. 6 "Alkaloids derived from tyrosine" (p. 336). |
| **indole.C₂N** | Trp skeleton without the carboxyl group (p. 11) | L-Trp, decarboxylated | L-Trp (6305). Tryptamine (1150) is in KEGG map01063 (checked). | lysergic acid (indole.C₂N + C₅ + C₁). Dewick ch. 6 "Alkaloids derived from tryptophan" (p. 366). |
| **C₄N** | A pyrrolidine ring. Ornithine "supplies not its α-amino nitrogen, but the δ-amino nitrogen", and loses its carboxyl group and α-N (p. 11). | L-ornithine (non-protein amino acid, from the Krebs cycle; p. 8) | L-Orn (6262). Putrescine (1045) is in [KEGG map01064](https://rest.kegg.jp/link/compound/map01064) (checked). Its role as the C₄N carrier is **[INFERENCE]** (Dewick ch. 6 "Polyamines", p. 311). | cocaine (C₄N + 2 × C₂ + (C₆C₁) + 2 × C₁) |
| **C₅N** | A piperidine ring. Same chemistry as C₄N; the ε-amino nitrogen is retained (p. 11). | L-lysine | L-Lys (5962). Cadaverine (273) is in KEGG map01064 (checked). Its role as the C₅N carrier is **[INFERENCE]**. | piperidine, quinolizidine and indolizidine alkaloids (Dewick ch. 6, pp. 326–330) |

**Other precursors Dewick lists that are not among the eight units:**

- **Sugars.** "Many secondary metabolites also contain one or more sugar units … such as glucose or ribose" (pp. 8–9). Molecules: D-glucose (5793). UDP-glucose (8629) is the donor in glycosylations such as quercetin → isoquercitrin ([KEGG R02158](https://rest.kegg.jp/get/R02158)) and is **already a coreactant** (`GLUCOSYL_DONOR_CoF`).
- **Other amino acids** drawn in Fig. 2.1 (p. 9): Gly, L-Ala, L-Val, L-Leu, L-Ile, L-Ser, L-Cys, L-Asp, L-Glu, L-Arg, L-Met. These feed peptides (ch. 7).
- **Further alkaloid precursors** with their own sections in Dewick ch. 6:
  - nicotinic acid (p. 331)
  - anthranilic acid (p. 395)
  - histidine (p. 398)
  - purines (p. 413)

  KEGG puts nicotinate in map01064, anthranilate in map01063 and His in map01065 (all checked).

## 2. Precursor-pathway table (by family)

All SMILES are PubChem's `SMILES` property. Each one was parsed with RDKit and its InChIKey matched PubChem (§5). A "coreactant" mark means the molecule is in `metacyc_coreactants.tsv` (MC) and/or `EnzymaticCoreactants.tsv` (EZ) (see §4.1).

### 2.1 Acetate–malonate (polyketide, fatty acid)

| Molecule | Role | CID | SMILES | Source / coreactant |
|---|---|---|---|---|
| acetyl-CoA | C₂ starter; also the source of mevalonate (Dewick p. 8) | [444493](https://pubchem.ncbi.nlm.nih.gov/compound/444493) | `CC(=O)SCCNC(=O)CCNC(=O)[C@@H](C(C)(C)COP(=O)(O)OP(=O)(O)OC[C@@H]1[C@H]([C@H]([C@@H](O1)N2C=NC3=C(N=CN=C32)N)O)OP(=O)(O)O)O` | KEGG map00061, map00900 (C00024). Coreactant: MC `ACETYL-COA`, EZ `cpd00022` |
| malonyl-CoA | C₂ extender; 3 × used by CHS ([KEGG R01613](https://rest.kegg.jp/get/R01613)) | [644066](https://pubchem.ncbi.nlm.nih.gov/compound/644066) | `CC(C)(COP(=O)(O)OP(=O)(O)OC[C@@H]1[C@H]([C@H]([C@@H](O1)N2C=NC3=C(N=CN=C32)N)O)OP(=O)(O)O)[C@H](C(=O)NCCC(=O)NCCSC(=O)CC(=O)O)O` | KEGG map00061 (C00083). **Not** a coreactant |

### 2.2 Shikimate / phenylpropanoid

| Molecule | Role | CID | SMILES | Source |
|---|---|---|---|---|
| phosphoenolpyruvate | Shikimate precursor (with E4P; Dewick p. 8) | [1005](https://pubchem.ncbi.nlm.nih.gov/compound/1005) | `C=C(C(=O)O)OP(=O)(O)O` | KEGG map00400 (C00074) |
| D-erythrose 4-phosphate | Shikimate precursor (Dewick p. 8) | [122357](https://pubchem.ncbi.nlm.nih.gov/compound/122357) | `C([C@H]([C@H](C=O)O)O)OP(=O)(O)O` | KEGG map00400 (C00279) |
| shikimic acid | Core intermediate (Dewick p. 8) | [8742](https://pubchem.ncbi.nlm.nih.gov/compound/8742) | `C1[C@H]([C@@H]([C@@H](C=C1C(=O)O)O)O)O` | KEGG map00400 (C00493) |
| chorismic acid | Branch point to Phe, Tyr, Trp and anthranilate | [12039](https://pubchem.ncbi.nlm.nih.gov/compound/12039) | `C=C(C(=O)O)O[C@@H]1C=C(C=C[C@H]1O)C(=O)O` | KEGG map00400 (C00251) |
| L-phenylalanine | C₆C₃, C₆C₂N | [6140](https://pubchem.ncbi.nlm.nih.gov/compound/6140) | `C1=CC=C(C=C1)C[C@@H](C(=O)O)N` | KEGG map00400, map00940 (C00079) |
| L-tyrosine | C₆C₃, C₆C₂N | [6057](https://pubchem.ncbi.nlm.nih.gov/compound/6057) | `C1=CC(=CC=C1C[C@@H](C(=O)O)N)O` | KEGG map00400 (C00082) |
| L-tryptophan | indole.C₂N | [6305](https://pubchem.ncbi.nlm.nih.gov/compound/6305) | `C1=CC=C2C(=C1)C(=CN2)C[C@@H](C(=O)O)N` | KEGG map00400 (C00078) |
| anthranilic acid | Quinazoline, quinoline and acridine alkaloids (Dewick ch. 6, p. 395) | [227](https://pubchem.ncbi.nlm.nih.gov/compound/227) | `C1=CC=C(C(=C1)C(=O)O)N` | KEGG map00400, map01063 (C00108) |
| trans-cinnamic acid | First C₆C₃ product (PAL) | [444539](https://pubchem.ncbi.nlm.nih.gov/compound/444539) | `C1=CC=C(C=C1)/C=C/C(=O)O` | KEGG map00940 (C00423) |
| p-coumaric acid | C₆C₃ (C4H product) | [637542](https://pubchem.ncbi.nlm.nih.gov/compound/637542) | `C1=CC(=CC=C1/C=C/C(=O)O)O` | KEGG map00940 (C00811) |
| p-coumaroyl-CoA | Activated C₆C₃; CHS starter | [6440013](https://pubchem.ncbi.nlm.nih.gov/compound/6440013) | `CC(C)(COP(=O)(O)OP(=O)(O)OC[C@@H]1[C@H]([C@H]([C@@H](O1)N2C=NC3=C(N=CN=C32)N)O)OP(=O)(O)O)[C@H](C(=O)NCCC(=O)NCCSC(=O)/C=C/C4=CC=C(C=C4)O)O` | KEGG map00940, map00941 (C00223) |
| benzoic acid | C₆C₁ **[INFERENCE: representative]** | [243](https://pubchem.ncbi.nlm.nih.gov/compound/243) | `C1=CC=C(C=C1)C(=O)O` | Dewick p. 11 (C₆C₁ concept) |
| 4-hydroxybenzoic acid | C₆C₁ **[INFERENCE: representative]** | [135](https://pubchem.ncbi.nlm.nih.gov/compound/135) | `C1=CC(=CC=C1C(=O)O)O` | Dewick p. 11 (C₆C₁ concept) |
| phenylacetic acid | C₆C₂ **[INFERENCE: representative]** | [999](https://pubchem.ncbi.nlm.nih.gov/compound/999) | `C1=CC=C(C=C1)CC(=O)O` | Dewick p. 11 (C₆C₂ concept) |

### 2.3 Mevalonate and MEP (isoprenoid)

| Molecule | Role | CID | SMILES | Source / coreactant |
|---|---|---|---|---|
| (R)-mevalonic acid | MVA pathway; from 3 × acetyl-CoA (Dewick p. 8) | [439230](https://pubchem.ncbi.nlm.nih.gov/compound/439230) | `C[C@@](CCO)(CC(=O)O)O` | KEGG map00900 (C00418) |
| pyruvic acid | MEP precursor (Dewick p. 8) | [1060](https://pubchem.ncbi.nlm.nih.gov/compound/1060) | `CC(=O)C(=O)O` | KEGG map00900 (C00022) |
| D-glyceraldehyde 3-phosphate | MEP precursor (Dewick p. 8) | [439168](https://pubchem.ncbi.nlm.nih.gov/compound/439168) | `C([C@H](C=O)O)OP(=O)(O)O` | KEGG map00900 (C00118) |
| 1-deoxy-D-xylulose 5-phosphate | MEP intermediate (Dewick p. 11) | [443201](https://pubchem.ncbi.nlm.nih.gov/compound/443201) | `CC(=O)[C@H]([C@@H](COP(=O)(O)O)O)O` | KEGG map00900 (C11437) |
| 2-C-methyl-D-erythritol 4-phosphate (MEP) | MEP pathway (Dewick p. 8) | [443198](https://pubchem.ncbi.nlm.nih.gov/compound/443198) | `C[C@](CO)([C@@H](COP(=O)(O)O)O)O` | KEGG map00900 (C11434) |
| isopentenyl diphosphate (IPP) | C₅ building block ([map00900](https://rest.kegg.jp/get/map00900)) | [1195](https://pubchem.ncbi.nlm.nih.gov/compound/1195) | `CC(=C)CCOP(=O)(O)OP(=O)(O)O` | KEGG map00900 (C00129). Coreactant: EZ `cpd00113` only |
| dimethylallyl diphosphate (DMAPP) | C₅ building block and prenyl donor (Dewick p. 12) | [647](https://pubchem.ncbi.nlm.nih.gov/compound/647) | `CC(=CCOP(=O)(O)OP(=O)(O)O)C` | KEGG map00900 (C00235). Coreactant: MC `PRENYL_DONOR_CoF` (CPD-4211), EZ `cpd00202` |

### 2.4 Amino-acid-derived (alkaloids, peptides)

| Molecule | Role | CID | SMILES | Source / coreactant |
|---|---|---|---|---|
| L-ornithine | C₄N | [6262](https://pubchem.ncbi.nlm.nih.gov/compound/6262) | `C(C[C@@H](C(=O)O)N)CN` | Dewick p. 8, 11. KEGG map01064 (C00077) |
| L-lysine | C₅N | [5962](https://pubchem.ncbi.nlm.nih.gov/compound/5962) | `C(CCN)C[C@@H](C(=O)O)N` | Dewick p. 8, 11. KEGG map01064 (C00047) |
| L-methionine | C₁ source via SAM | [6137](https://pubchem.ncbi.nlm.nih.gov/compound/6137) | `CSCC[C@@H](C(=O)O)N` | Dewick pp. 10, 12 |
| L-histidine | Imidazole alkaloids (Dewick p. 398) | [6274](https://pubchem.ncbi.nlm.nih.gov/compound/6274) | `C1=C(NC=N1)C[C@@H](C(=O)O)N` | KEGG map01065 (C00135). Coreactant: EZ `cpd00119` |
| nicotinic acid | Pyridine alkaloids (Dewick p. 331) | [938](https://pubchem.ncbi.nlm.nih.gov/compound/938) | `C1=CC(=CN=C1)C(=O)O` | KEGG map01064 (C00253) |
| tyramine | C₆C₂N carrier | [5610](https://pubchem.ncbi.nlm.nih.gov/compound/5610) | `C1=CC(=CC=C1CCN)O` | KEGG map01063 (C00483) |
| dopamine | C₆C₂N carrier | [681](https://pubchem.ncbi.nlm.nih.gov/compound/681) | `C1=CC(=C(C=C1CCN)O)O` | KEGG map01063 (C03758) |
| tryptamine | indole.C₂N carrier | [1150](https://pubchem.ncbi.nlm.nih.gov/compound/1150) | `C1=CC=C2C(=C1)C(=CN2)CCN` | KEGG map01063 (C00398) |
| putrescine | C₄N carrier **[INFERENCE: role]** | [1045](https://pubchem.ncbi.nlm.nih.gov/compound/1045) | `C(CCN)CN` | KEGG map01064 (C00134) |
| cadaverine | C₅N carrier **[INFERENCE: role]** | [273](https://pubchem.ncbi.nlm.nih.gov/compound/273) | `C(CCN)CCN` | KEGG map01064 (C01672) |

### 2.5 Carbohydrate and cofactor-type donors

| Molecule | Role | CID | SMILES | Source / coreactant |
|---|---|---|---|---|
| D-glucose | Sugar units of glycosides (Dewick pp. 8–9) | [5793](https://pubchem.ncbi.nlm.nih.gov/compound/5793) | `C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O` | Dewick Fig. 2.1 |
| UDP-glucose | Glucosyl donor (e.g. [KEGG R02158](https://rest.kegg.jp/get/R02158)) | [8629](https://pubchem.ncbi.nlm.nih.gov/compound/8629) | `C1=CN(C(=O)NC1=O)[C@H]2[C@@H]([C@@H]([C@H](O2)COP(=O)(O)OP(=O)(O)O[C@@H]3[C@@H]([C@H]([C@@H]([C@H](O3)CO)O)O)O)O)O` | Coreactant: MC `GLUCOSYL_DONOR_CoF` (CPD-12575) |
| S-adenosylmethionine (SAM) | C₁ methyl donor (Dewick p. 12) | [34755](https://pubchem.ncbi.nlm.nih.gov/compound/34755) | `C[S+](CC[C@@H](C(=O)[O-])N)C[C@@H]1[C@H]([C@H]([C@@H](O1)N2C=NC3=C(N=CN=C32)N)O)O` | Coreactant: MC `METHYL_DONOR_CoF`, EZ `cpd00017` |
| 2-oxoglutaric acid | Co-substrate of F3H and FLS ([KEGG R02444](https://rest.kegg.jp/get/R02444), [R02160](https://rest.kegg.jp/get/R02160)) | [51](https://pubchem.ncbi.nlm.nih.gov/compound/51) | `C(CC(=O)O)C(=O)C(=O)O` | Coreactant: MC `CARBONYL_CoF`, EZ `cpd00024` |

## 3. Quercetin route

### 3.1 Mapping quercetin onto building units

- The KEGG map00941 description says: "condensation of p-coumaroyl-CoA (C6-C3) with three malonyl-CoA (C3) molecules results in naringenin chalcone with a diphenylpropane (C6-C3-C6) unit, which is converted to naringenin" ([map00941](https://rest.kegg.jp/get/map00941)).
- In Dewick's units this is **1 × C₆C₃ + 3 × C₂**. Each malonyl-CoA loses its CO₂, so it adds a C₂ unit (Dewick p. 10; Fig. 2.3 p. 12, naringin = C₆C₃ + 3 × C₂ + sugars).
- **Carbon count:** 9 C (C₆C₃) + 6 C (3 × C₂) = 15 C = C₁₅H₁₀O₇ (quercetin, CID 5280343).
- **Atom assignment** **[INFERENCE, standard flavonoid numbering]**:
  - The C₆C₃ unit gives the B ring plus C2, C3 and C4 of the C ring.
  - The three C₂ units give the A ring (C4a, C5–C8, C8a).
- **Later modifications:** the 3-OH comes from F3H, the 3′-OH from F3′H, and the C2=C3 double bond from FLS.

### 3.2 Steps, enzymes and IDs

| # | Reaction | Enzyme (EC) | KEGG | MetaCyc reaction |
|---|---|---|---|---|
| 1 | L-Phe → trans-cinnamate + NH₃ | PAL (4.3.1.24/25) | [R00697](https://rest.kegg.jp/get/R00697) | [PHENYLALANINE-AMMONIA-LYASE-RXN](https://biocyc.org/reaction?orgid=META&id=PHENYLALANINE-AMMONIA-LYASE-RXN) |
| 2 | cinnamate + O₂ + NADPH-P450 reductase → 4-coumarate | C4H (1.14.14.91) | [R02253](https://rest.kegg.jp/get/R02253) | [TRANS-CINNAMATE-4-MONOOXYGENASE-RXN](https://biocyc.org/reaction?orgid=META&id=TRANS-CINNAMATE-4-MONOOXYGENASE-RXN) |
| 3 | 4-coumarate + CoA + ATP → p-coumaroyl-CoA + AMP + PPi | 4CL (6.2.1.12) | [R01616](https://rest.kegg.jp/get/R01616) | [4-COUMARATE--COA-LIGASE-RXN](https://biocyc.org/reaction?orgid=META&id=4-COUMARATE--COA-LIGASE-RXN) |
| 4 | p-coumaroyl-CoA + **3 malonyl-CoA** → naringenin chalcone + 4 CoA + 3 CO₂ | CHS (2.3.1.74) | [R01613](https://rest.kegg.jp/get/R01613) | [NARINGENIN-CHALCONE-SYNTHASE-RXN](https://biocyc.org/reaction?orgid=META&id=NARINGENIN-CHALCONE-SYNTHASE-RXN) |
| 5 | naringenin chalcone → (2S)-naringenin | CHI (5.5.1.6) | [R02446](https://rest.kegg.jp/get/R02446) | [APIGNAR-RXN](https://biocyc.org/reaction?orgid=META&id=APIGNAR-RXN) |
| 6 | naringenin + 2-OG + O₂ → dihydrokaempferol + succinate + CO₂ | F3H (1.14.11.9) | [R02444](https://rest.kegg.jp/get/R02444) | [NARINGENIN-3-DIOXYGENASE-RXN](https://biocyc.org/reaction?orgid=META&id=NARINGENIN-3-DIOXYGENASE-RXN) |
| 7 | dihydrokaempferol + O₂ + NADPH-P450 reductase → taxifolin (dihydroquercetin) | F3′H (1.14.14.82) | [R03124](https://rest.kegg.jp/get/R03124) | [RXN-525](https://biocyc.org/reaction?orgid=META&id=RXN-525) |
| 8 | taxifolin + 2-OG + O₂ → quercetin + succinate + CO₂ + H₂O | FLS (1.14.20.6) | [R02160](https://rest.kegg.jp/get/R02160) | [RXN-527](https://biocyc.org/reaction?orgid=META&id=RXN-527) |

Notes on the step table:

- **Pathway grouping.** KEGG module [M00137](https://rest.kegg.jp/get/M00137) "Flavanone biosynthesis, phenylalanine => naringenin" lists steps 1–5 (PAL, C4H, 4CL, CHS, CHI).
- **Equivalent orderings, also 8 steps from Phe:**
  - FLS on dihydrokaempferol → kaempferol ([RXN1F-93](https://biocyc.org/reaction?orgid=META&id=RXN1F-93), KEGG R03126), then F3′H kaempferol → quercetin ([RXN-12510](https://biocyc.org/reaction?orgid=META&id=RXN-12510), KEGG R06538). MetaCyc [flavonol biosynthesis (PWY-3101)](https://biocyc.org/pathway?orgid=META&id=PWY-3101) describes this grid: flavonols come from dihydroflavonols via 2-oxoglutarate-dependent FLS, and "3'-hydroxylation of kaempferol to yield quercetin … adds another connection".
  - F3′H on naringenin → eriodictyol ([RXN-7652](https://biocyc.org/reaction?orgid=META&id=RXN-7652)), then F3H → taxifolin ([RXN-7775](https://biocyc.org/reaction?orgid=META&id=RXN-7775)).
- **KEGG pathway membership.** R01613, R02446, R02444, R03124 and R02160 are in `rn00941` Flavonoid biosynthesis. R06538 is also in `rn00944` (KEGG REST `PATHWAY` fields).

**Minimum generations:**

| Starting compound | Minimum `-g` |
|---|---|
| L-Phe | 8 |
| p-coumaric acid | 6 |
| naringenin chalcone | 4 |
| naringenin | 3 |

A shortcut from L-Tyr exists: tyrosine ammonia-lyase converts Tyr → 4-coumarate in one step ([KEGG R00737](https://rest.kegg.jp/get/R00737), EC 4.3.1.23). That gives 7 steps from Tyr. That the generic PAL rule `rule0244` also fires on Tyr is **[INFERENCE]**; not run.

## 4. Repo cross-check (no repo code was modified)

### 4.1 Building blocks that are already coreactants

| Building block | `metacyc_coreactants.tsv` (used by `--metacyc_rules`) | `EnzymaticCoreactants.tsv` |
|---|---|---|
| acetyl-CoA | `ACETYL-COA` | `cpd00022` AcetylCoa |
| CoA | `CoA` (CO-A) | `cpd00010` |
| **malonyl-CoA** | `MALONYL-COA` (added after this note's analysis, §4.2 point 6) | **absent** |
| SAM / SAH | `METHYL_DONOR_CoF` / `METHYL_ACCEPTOR_CoF` | `cpd00017` / `cpd00019` |
| DMAPP | `PRENYL_DONOR_CoF` (CPD-4211, SMILES `CC(C)=CCOP(=O)(O)OP(=O)(O)O`) | `cpd00202` |
| IPP | absent | `cpd00113` |
| UDP-glucose / UDP | `GLUCOSYL_DONOR_CoF` (CPD-12575) / `GLUCOSYL_ACCEPTOR_CoF` | absent |
| ATP / AMP / ADP / PPi / Pi | present (`PYROPHOSPHATE_*`, `PHOSPHATE_*`, `PPI`, `Pi`) | present |
| NADP(H) | `NAD_CoF` = NADP, `NADH_CoF` = NADPH | NAD⁺/NADH (`cpd00003`/`cpd00004`) |
| O₂, H₂O, CO₂, NH₃ | present | present |
| 2-oxoglutarate / glutamate | `CARBONYL_CoF` / `AMINO_CoF` | `cpd00024` / `cpd00023` |
| L-histidine, indole, phenol | absent | present (`cpd00119`, `cpd00359`, `cpd00127`) |

Source: `cut -f1,2` on both files. Metacyc file: 44 coreactants; Enzymatic file: 32.

**Consequences for the starting set:**

- **No need to add coreactants.** SAM, acetyl-CoA, CoA, DMAPP, UDP-glucose, ATP, NADPH, O₂ and 2-OG are supplied automatically as coreactants.
- **Adding one anyway creates a duplicate pool entry.** A molecule loaded both as a coreactant and a starting compound gets a different hash prefix: `X` for coreactants, `C` for starting/predicted compounds (`mine_database/utils.py:125-165`). It would then be expanded as an ordinary compound too **[INFERENCE from code; not run]**.

### 4.2 How CHS (3 × malonyl-CoA) is, and is not, encoded

1. **No generalized rule maps CHS.** `NARINGENIN-CHALCONE-SYNTHASE-RXN` does not appear in `mine_database/data/metacyc_rules/metacyc21_coverage.tsv`, the reaction→rule map that `rules.py:101` uses to rank and select rules (`grep` returned nothing).
   - The same file does map the other route steps: PAL `rule0244`, C4H `rule0005`/`rule0004`, 4CL `rule0038`/`rule0039`, CHI `APIGNAR-RXN` → `rule0093`, F3H → `rule0044`/`rule0045`, F3′H `RXN-525` → `rule0005`/`rule0004`, FLS `RXN-527` → `rule0323`/`rule0192`.
   - The rule file has no reactant slot named malonyl-CoA at all (reactant-pattern census of `metacyc_generalized_rules.tsv`).
2. **"Any" slots cannot pair two different pool compounds.**
   - `reactions.py:32-34` says: "Full Operators … use a single supplied molecule for all 'Any' instances in the rule."
   - `reactions.py:277-279` builds the reactant tuple as `mol if x == "Any" else coreactant_mols[x][0]`.
   - So a hypothetical `Any;Any;Any;Any` CHS rule would get four copies of p-coumaroyl-CoA, not one p-coumaroyl-CoA plus three malonyl-CoA.
   - The partial-operator path that would allow different `Any` partners is commented out (`reactions.py:410-460`, "TODO: Partial operators aren't used").
3. **Answer: putting malonyl-CoA in the starting set does not enable CHS.**
   - Malonyl-CoA is not a coreactant. In a starting file it is only expanded on its own.
   - To get CHS you would need either a dedicated rule that names malonyl-CoA as a coreactant slot (add it to the coreactant list), or a run that starts downstream of CHS (naringenin chalcone or naringenin). **[INFERENCE: proposed workaround, not implemented here]**
4. **The same "Any" problem affects the 2-OG dioxygenases.** In the generalized rules, F3H and FLS carry 2-oxoglutarate as a second `Any`, not as `CARBONYL_CoF`:
   - `rule0045`: `Any;Any;O2 >> Any;Any;CO2`
   - `rule0192`: `Any;Any;O2 >> Any;Any;CO2;WATER`

   2-OG therefore cannot fill that slot either. In the test (§4.4), F3H was still reproduced, but by the generic NADPH/O₂ hydroxylation `rule0004`. FLS was not reproduced.
5. **Possible direction mislabel (no effect here).**
   - The coverage file maps forward `TRANS-CINNAMATE-4-MONOOXYGENASE-RXN` to `rule0005`, but `rule0005`'s SMARTS is a de-hydroxylation (`Any;NAD_CoF;WATER >> Any;NADH_CoF;O2`). The hydroxylation is `rule0004`.
   - The pairs F3H→`rule0044` and FLS→`rule0323` show the same pattern.
   - Both directions are separate rules and both are among the first 244, so this does not affect the run below.
6. **Implemented workaround.** `MALONYL-COA` was added to `metacyc_coreactants.tsv`, and `rule_CHS` (`Any;MALONYL-COA;MALONYL-COA;MALONYL-COA >> Any;CoA;CoA;CoA;CoA;CO2;CO2;CO2`) to `metacyc_custom_rules.tsv`. Load it next to the generalized rules by repeating `-r`. In a CLI run from p-coumaric acid with `rule0039` + `rule_CHS` (2 generations, implicit H), Pickaxe recorded `(1) p-coumaroyl-CoA + (3) MALONYL-COA >> (1) naringenin chalcone + (4) CoA + (3) CO2`. With `--explicit_h` the rule produces nothing, because it is written in implicit-H form like the generalized rules.
7. **FLS rule.** `SUCCINATE` was added to `metacyc_coreactants.tsv`, and `rule_FLS` (`Any;CARBONYL_CoF;O2 >> Any;SUCCINATE;CO2;WATER`) to `metacyc_custom_rules.tsv`. It names 2-oxoglutarate (`CARBONYL_CoF`) explicitly instead of the second `Any` of `rule0192`, and only matches a 2-aryl-3-hydroxy-chroman-4-one (ring O–CH(aryl)–CH(OH)–C=O). The product carbons are written `[#6H0]` because Pickaxe keeps stereochemistry (`RemoveStereochemistry` is commented out, `pickaxe_commons.py:316`), and a `[C@H]` centre would otherwise keep its H and fail valence. CLI checks: taxifolin → quercetin in 1 generation; from naringenin chalcone with `rule0093` + `rule0004` + `rule_FLS`, quercetin was found after 4 generations (pruned network: 17 compounds, 15 reactions, both the taxifolin and the kaempferol branch).

### 4.3 Input format and rule selection

- **File type.** `-c/--compound_file` and `-t/--target_file` take `.csv`, `.tsv` or `.json`, chosen by substring of the file name (`utils.py:85-95`).
- **ID column.** It must be called `id` (`load_compound_set(…, id_field="id")`, `pickaxe_commons.py:277-279`; same for `load_targets`).
- **Structure column.** The first column whose lower-cased name is `smiles`, `inchi` or `structure` is used. Values containing `InChI=` are parsed as InChI (`_mol_from_dict`, `pickaxe_commons.py:465-481`).
- **Compounds that are dropped:**
  - Starting compounds whose SMILES has no `C`/`c` (inorganics), `pickaxe_commons.py:317-318`. Targets need a `c`/`C` (line 270).
  - Disconnected molecules (salts), because `fragmented_mols` is `False` (lines 170, 491).
  - Charges are neutralised by default (`-n` default `True`).
- **Rule count needed.** `--metacyc_rules general` needs `--rule_count` or `--rule_coverage`. Rules are taken in file order (`rules.py:153-202`). Computed positions of the route rules:

| Rule | Step | Position | Cumulative coverage |
|---|---|---|---|
| `rule0004` | hydroxylation (C4H/F3H/F3′H) | 4 | 0.146 |
| `rule0039` | 4CL | 39 | 0.535 |
| `rule0045` | F3H as written | 45 | 0.562 |
| `rule0093` | CHI | 93 | 0.693 |
| `rule0192` | FLS as written | 192 | 0.805 |
| `rule0244` | PAL | 244 | 0.8375 |

  **`--rule_count 244` (or `--rule_coverage 0.84`) is the smallest selection containing every route rule that exists.** In total 1,216 rules are selectable.

### 4.4 Pickaxe step test (1 generation per step, all 1,216 generalized rules, `processes=1`)

Each substrate was added alone with `_add_compound`. The product was searched by the InChIKey connectivity block (first 14 characters).

| Step | Product found? | Producing rule(s) | Compounds after 1 gen | Time |
|---|---|---|---|---|
| PAL: Phe → cinnamate | **yes** | `rule0244`, `rule0302` | 461 | 2.6 s |
| C4H: cinnamate → p-coumarate | **yes** | `rule0004` (+ others) | 426 | 2.5 s |
| 4CL: p-coumarate → p-coumaroyl-CoA | **yes** | `rule0039` (+ others) | 489 | 3.6 s |
| CHS: p-coumaroyl-CoA → naringenin chalcone | **no** | — | 6,904 | 385 s (hit RDKit `maxProducts=10000`) |
| CHI: naringenin chalcone → naringenin | **yes** | `rule0093` | 875 | 13.5 s |
| F3H: naringenin → dihydrokaempferol | **yes** | `rule0004` (+ others) | 1,005 | 13.9 s |
| F3′H: dihydrokaempferol → taxifolin | **yes** | `rule0004` (+ others) | 1,140 | 15.8 s |
| FLS: taxifolin → quercetin | **no** | — | 1,531 | 17.6 s |
| FLS: dihydrokaempferol → kaempferol | **no** | — | 1,140 | 15.8 s |
| F3′H: kaempferol → quercetin | **yes** | `rule0004` (+ others) | 702 | 12.8 s |

**Conclusions from the test:**

- **Cinnamate check passed.** The requested quick check (Phe → cinnamate in one generation) succeeds.
- **The full run is broken at CHS and FLS.** Quercetin is not reachable from Phe in a straight run.
- **Two generations from taxifolin were not run.** A 2-generation expansion from taxifolin (about 1,500 compounds × 1,216 rules) was skipped as too slow; extrapolated from about 15 s per compound per generation, it would take hours **[INFERENCE]**. So whether some longer detour reaches quercetin is unknown.
- **Combinatorial cost.** CoA thioesters (p-coumaroyl-CoA, and by extension malonyl-CoA) are very expensive to expand with generalized rules (385 s and 6,904 compounds for one molecule, one generation).

### 4.5 Suggested commands

Run from the repo root. Create the output directory first. The CSVs are in §6.

```bash
mkdir -p runs/quercetin_phe
uv run mine_database/pickaxe_commons.py \
  -c runs/start_quercetin_minimal.csv \
  -t runs/target_quercetin.csv --prune_to_targets \
  --metacyc_rules general --rule_count 244 \
  -g 8 -m 8 -o runs/quercetin_phe
```

**Expected outcome (from §4.4): no quercetin, because of the CHS and FLS gaps** **[INFERENCE for the 8-generation run itself; not executed]**.

- **Network size.** One generation from Phe already gives 461 compounds. Eight generations is very likely intractable without pruning between generations **[INFERENCE]**.
- **Tests that isolate rule coverage from search depth:**
  - start from naringenin chalcone with `-g 4`
  - start from naringenin with `-g 3`

  Use the full building-block set (§6) only for broad exploratory runs at `-g 1`–`2`.

## 5. RDKit validation (done)

- **Script:** `/tmp/bb/validate.py`, run with `uv run python` in this repo (RDKit 2024.03.6). Not added to the repo.
- **Check:** for each of the 44 PubChem records cited in this note, `Chem.MolFromSmiles` succeeded and `MolToInchiKey` equalled PubChem's InChIKey. Result: **44/44**. The 44 are the 37 molecules in §2 plus 7 route compounds: naringenin chalcone 5280960, (2S)-naringenin 439246, dihydrokaempferol 122850, taxifolin 439533, kaempferol 5280863, (+)-eriodictyol 440735 and quercetin 5280343.
- **Corrected PubChem picks:**
  - The first PubChem pick for DXP (CID 443200) turned out to be 4-CDP-2-C-methyl-D-erythritol 2-phosphate. It was replaced by CID 443201.
  - Racemic G3P (CID 729) was replaced by D-G3P (CID 439168).
- **CSV loading:** the CSV blocks below were loaded through `Pickaxe.load_compound_set` and `Pickaxe.load_targets`. Result: "16 compounds loaded", "1 compounds loaded", "1 target compounds loaded".

## 6. Ready-to-copy CSV blocks

### 6.1 Recommended building-block starting set (`start_building_blocks.csv`)

- **Contents:** one or more representatives for each Dewick unit and precursor family.
- **Excluded:** molecules that are already MetaCyc coreactants (acetyl-CoA, SAM, DMAPP, UDP-glucose, 2-OG, CoA).
- **Malonyl-CoA:** now a coreactant (`MALONYL-COA`, §4.2 point 6), so it is no longer part of the starting set.

```csv
id,SMILES
L-phenylalanine,C1=CC=C(C=C1)C[C@@H](C(=O)O)N
L-tyrosine,C1=CC(=CC=C1C[C@@H](C(=O)O)N)O
L-tryptophan,C1=CC=C2C(=C1)C(=CN2)C[C@@H](C(=O)O)N
L-ornithine,C(C[C@@H](C(=O)O)N)CN
L-lysine,C(CCN)C[C@@H](C(=O)O)N
L-methionine,CSCC[C@@H](C(=O)O)N
L-histidine,C1=C(NC=N1)C[C@@H](C(=O)O)N
anthranilic_acid,C1=CC=C(C(=C1)C(=O)O)N
nicotinic_acid,C1=CC(=CN=C1)C(=O)O
shikimic_acid,C1[C@H]([C@@H]([C@@H](C=C1C(=O)O)O)O)O
chorismic_acid,C=C(C(=O)O)O[C@@H]1C=C(C=C[C@H]1O)C(=O)O
R-mevalonic_acid,C[C@@](CCO)(CC(=O)O)O
MEP,C[C@](CO)([C@@H](COP(=O)(O)O)O)O
IPP,CC(=C)CCOP(=O)(O)OP(=O)(O)O
D-glucose,C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O
```

### 6.2 Minimal starting set for the quercetin test (`start_quercetin_minimal.csv`)

```csv
id,SMILES
L-phenylalanine,C1=CC=C(C=C1)C[C@@H](C(=O)O)N
```

### 6.3 Target (`target_quercetin.csv`)

```csv
id,SMILES
quercetin,C1=CC(=C(C=C1C2=C(C(=O)C3=C(C=C(C=C3O2)O)O)O)O)O
```

## 7. Open questions and limitations

- **Dewick access.** Only chapter 2 and the table of contents were read (publisher sample). The chapter 4 (flavonoids, p. 167) and chapter 6 details are cited only through the table of contents.
- **Garbled figure text.** The labels in Fig. 2.3 were extracted from PDF text and were somewhat jumbled. The unit assignments quoted above are my reading of that text **[INFERENCE where the label order was ambiguous: THCA = 6 × C₂ + 2 × C₅; papaverine = C₆C₂N + (C₆C₂) + 4 × C₁]**.
- **Rule version.** MetaCyc reaction IDs were checked on MetaCyc 30.0. The repo rules come from MetaCyc 21 (`metacyc21_coverage.tsv`), and IDs may have been renamed in between. CHS has had the same ID (`NARINGENIN-CHALCONE-SYNTHASE-RXN`) but is absent from the v21 coverage map. Whether CHS was excluded upstream (e.g. as a multi-substrate reaction) is **[INFERENCE: unverified]**.
- **Unverified alternative detours.** The FLS gap was tested only for one generation. Whether a multi-step detour reaches quercetin (for example 3-OH oxidation followed by tautomerisation) is unknown. Pickaxe does not tautomerise products except through `postsanitize_smiles` for N-containing SMILES (`pickaxe_commons.py:320-321, 522-523`).
- **Original rule set not tested.** `EnzymaticReactionRules.tsv` (250 rules, explicit-H SMARTS) was not tested on the route. It uses acetyl-CoA (`cpd00022`) in 6 rules and 2-OG (`cpd00024`) in 2 (reactant-slot census). It has no malonyl-CoA coreactant either.
- **Representative molecules are a choice.** Benzoic acid, phenylacetic acid, putrescine and cadaverine are my picks for the C₆C₁, C₆C₂, C₄N and C₅N units, not quotations from Dewick.
