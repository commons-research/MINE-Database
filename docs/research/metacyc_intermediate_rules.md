# What is `metacyc_intermediate_rules.tsv`?

Research note, 2026-10-15. This note covers `mine_database/data/metacyc_rules/metacyc_intermediate_rules.tsv`: what it is, where it comes from, how it differs from `metacyc_generalized_rules.tsv`, and how this repo uses it.
Claims that were not observed directly in a source or computed from the files are marked **[INFERENCE]**.

## TL;DR

- **The paper is not Sun et al.** DOI `10.1016/j.ymben.2021.02.006` is **Ni Z, Stine AE, Tyo KEJ, Broadbelt LJ, "Curating a comprehensive set of enzymatic reaction rules for efficient novel biosynthetic pathway design", *Metabolic Engineering* 65:79–87 (2021)** ([Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1016/j.ymben.2021.02.006&format=json&resultType=core), [OSTI accepted manuscript](https://www.osti.gov/servlets/purl/1852562)). Pickaxe ([Shebek et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10031857/)) and MINE 2.0 ([Strutz et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9237697/)) are separate papers that use this rule set.
- **Generalized rules (`metacyc_generalized_rules.tsv`) = JN1224min.** These are the 1,224 rules from Ni et al. 2021. Each rule describes only the **reaction center**, meaning the atoms whose bonds change. The file is byte-identical to DORAnet's `JN1224MIN_rules.tsv` (checked with `cmp`, see §5).
- **Intermediate rules (`metacyc_intermediate_rules.tsv`) are not described in the Ni 2021 paper.** The word "intermediate" does not appear in the manuscript text (§5). They are an unpublished in-house Tyo/Broadbelt rule set, added upstream on 2021-03-16. Its published descendant is **JN3604imt**, which DORAnet describes as "a larger set of rules with optimized intermediate specificity" and attributes to Ni's 2022 PhD thesis ([DORAnet, Zhang et al. 2025, §4.1](https://pmc.ncbi.nlm.nih.gov/articles/PMC12512011/)).
- **What an intermediate rule is.** It is a generalized rule whose reaction-center atoms carry recursive-SMARTS context.
  - The context has two parts: `$(...)` gives the chemical environment that the substrates of one reaction cluster share, and `!$(...)` excludes environments that belong to sibling clusters.
  - Each generalized rule is therefore split into one or more substrate-specific sub-rules (named `ruleNNNN_k`). Each sub-rule covers a disjoint subset of the known reactions.
  - On the specificity spectrum, these rules sit between "reaction center only" (generalized) and "whole molecule" (one rule per reaction). That is why they are called "intermediate" (all of this is computed in §3).
- **How this repo uses them.** `mine_database/rules.py:287-440` (`metacyc_intermediate`) picks subsets by number of rules or by fraction of covered reactions. The CLI in `pickaxe_commons.py` exposes this as `--metacyc_rules intermediate` (lines 1508-1563). The documented LOTUS runs in `README.md` use the **generalized** rules instead.

## 1. Specificity spectrum: generalized vs intermediate

| | Generalized (JN1224min) | Intermediate (this file) |
|---|---|---|
| What the SMARTS encodes | Reaction-center atoms only, e.g. `rule0012`: `[#6:1]-[#8:2].[#7:3]>>[#6:1]-[#7:3].[#8:2]` (`metacyc_generalized_rules.tsv`, row `rule0012`) | The same reaction center, plus `$(...)`/`!$(...)` environments on the reaction-center atoms. Example `rule0012_18`: atom 1 must sit in a Gly-like `C(=O)CNC=O` context and must not be in a Pro-Gly context (`metacyc_intermediate_rules.tsv:2`) |
| Rule count | 1,224 (1,225 lines including the header; `wc -l`) | 7,358 (7,359 lines; `wc -l`) |
| Median SMARTS length | 76 characters | 486 characters (computed with pandas) |
| Rows with recursive SMARTS `$(` | 0% | 91.6%. 45.4% also contain `!$(` (computed) |
| Reactions grouped per rule | Many. All reactions that share a reaction center ([Ni 2021 §2.4, p. 9](https://www.osti.gov/servlets/purl/1852562)) | Mean 10.1, median 4, max 989 (`counts` column) |
| Promiscuity in expansions | Maximal by design ([MINE 2.0 §2.1](https://pmc.ncbi.nlm.nih.gov/articles/PMC9237697/): "designed to maximize potential promiscuity") | Lower, aimed at "more realistic promiscuity" ([DORAnet §4.1](https://pmc.ncbi.nlm.nih.gov/articles/PMC12512011/), said of JN3604imt) |

### How the generalized rules were made (published)

Source: Ni et al. 2021, OSTI accepted manuscript ([link](https://www.osti.gov/servlets/purl/1852562)).

- **Input data (§2.1–2.2, pp. 6–7).** The input was atom-mapped reactions from MetaCyc v21.0. Reactions with missing structures or broken atom balance were removed, as were cofactor-only, transport and racemization reactions. "Both the forward and reverse reaction directions were considered."
- **Rule extraction (§2.4, p. 9).** "all non-hydrogen atoms involved in bond changes were identified as part of the reaction center" and written as SMARTS with RDKit. "Those reactions that produced the same reaction rule, with identical reaction SMARTS and cofactor designation, were grouped together."
- **Pruning (§3.2, pp. 13–16).** 4,722 raw rules were reduced to 2,318 by removing atom-mapping redundancies (1,583 rules) and resonance errors (735). A further filter removed rules with more than 15 reaction-center atoms, more than 7 species, or more than 1 uncommon heavy atom (1,157 rules).
- **Final set (§3.3, pp. 17–18).** 1,224 rules "mapped more than one unique reaction across different metabolic databases", and 1,094 "singleton" rules were set aside. Supplement A holds the 1,224 rules and Supplement B the 2,318 rules.
- **Future work (Conclusion, p. 22).** The paper only names more specific rules as future work: "reaction rules that consider moieties within a certain radius around the reaction center could increase the specificity of predicted reactions, and narrow down known candidate enzymes to be evaluated."

### How the intermediate rules were made (what is known)

- **No paper or code describes the method.**
  - The upstream repo has no generation code, only selection code and a selection notebook. The notebook is `example_data/metacyc_rule_selection/intermediate_from_generalized_rule_sel.ipynb`, added upstream and deleted in tyo-nu commit `38f53b6957` (2021-06-10). Its cells only select rows by name pattern from the finished TSV.
  - DORAnet cites Ni's thesis for JN3604imt ([DORAnet ref. 30](https://pmc.ncbi.nlm.nih.gov/articles/PMC12512011/): "Ni Z., PhD thesis, Northwestern University, 2022").
  - Pate et al. describe the related "Pathway-level clustering" rule set (3,597 templates) as follows: "constructed by first clustering reactions with similar reactant structures and then writing a reaction rule which includes the maximum common subgraph of all reactions grouped into a cluster. For more details see Ni, 2022" ([Pate, Tyo, Broadbelt 2026, Methods "Assembling reaction rules"](https://pmc.ncbi.nlm.nih.gov/articles/PMC13228424/); thesis title in their ref. 41: *Data-Driven Approaches to Predict and Utilize Enzyme Promiscuity for Novel Biosynthesis Design*). No open copy of the thesis was found online.
- **What the file itself shows (computed; scripts are in "Reproduction" below):**
  1. **Every intermediate row is a child of exactly one generalized rule.** If the `$(...)`/`!$(...)` blocks are removed from an intermediate SMARTS, the remaining SMARTS plus its Reactants/Products columns equals exactly one generalized rule. This holds for all 7,358 rows.
  2. **Children cover the parents almost completely.** 1,221 of the 1,224 generalized rules have children. `rule0462`, `rule0463` and `rule0977` have none. The number of children per parent has median 1, mean 6.0 and max 233 (`rule0013`).
  3. **Environments are only on the reactant side.** 12,964 mapped reactant atoms carry environments. Each of those atoms has at most one positive `$(...)` environment. No product-side atom has one.
  4. **Negative environments are sibling exclusions.** All 42,042 `!$(...)` blocks are identical to the positive `$(...)` environment of a **sibling** intermediate rule (same parent) on the same mapped atom. In a sample of 3,000 (positive, negative) pairs, at least 2,401 negative environments are strictly larger than the rule's own positive environment and contain it. RDKit query-vs-query matching is approximate, so 2,401 is a lower bound. In other words, a broader cluster says "match my common substructure, except where a more specific sibling cluster applies". **[INFERENCE]** This resembles a hierarchy, i.e. disjoint clusters ordered from specific to general, similar in spirit to the Hasse-diagram templates of EHreact. The algorithm has not been confirmed from a primary source.
  5. **The reactions are partitioned.** The `Comments` column lists 74,159 reaction IDs, and none repeats across rows. So each known reaction is assigned to exactly one intermediate rule.
  6. **RDKit check on 400 sampled intermediate rules** (parents ≤ `rule1000`, with environments), using the reaction SMILES in the historical upstream mapping file (§2). Only the non-cofactor (`Any`) reactant templates were tested, on either reaction side:
     - the intermediate templates match **1,380/1,435** (96%) of their own member reactions;
     - the parent generalized templates match **1,435/1,435**;
     - the intermediate templates match only **162/3,034** (5%) of reactions belonging to sibling clusters.

     So the intermediate rules are strictly more selective than their parent but still mostly reproduce their own reactions.

## 2. File format and statistics

All files in `mine_database/data/metacyc_rules/` are byte-identical to `tyo-nu/MINE-Database` master. Local `git hash-object` equals the upstream GitHub contents-API `sha` for all five TSVs (e.g. intermediate = `2a4fad2537d445cffaf34728863743cde1c28943`).

### `metacyc_intermediate_rules.tsv` (7,358 rules, 15.5 MB)

| Column | Meaning | Evidence / stats |
|---|---|---|
| `Name` | `ruleNNNN_k` = intermediate child *k* of generalized rule `ruleNNNN`. 611 rows have no `_k` suffix: they carry no environment and equal a generalized rule exactly | 615 rows have no `$(`. 7,052 rows have a prefix that equals their true parent's name. See "Naming caveat" below |
| `Reactants`, `Products` | `;`-separated slots: `Any` or a cofactor ID from `metacyc_coreactants.tsv`. Same format as the generalized file | Read by `pickaxe.py:402-411` |
| `SMARTS` | Reaction SMARTS with recursive environments on the reactant-side mapped atoms | §1 |
| `Comments` | IDs of the known reactions grouped in this rule, prefixed `metacyc:`, `kegg:` or `brenda:` | ID prefixes: brenda 45,684, metacyc 17,538, kegg 10,739, unprefixed 198 |
| `counts` | Number of reactions in the cluster | Equals the number of IDs in `Comments` for 7,327/7,358 rows. The file is sorted by `counts`, descending (`sort -c -n -r` on column 6 passes). Sum 74,449 |
| `Uniprot` | UniProt/gene IDs of the enzymes linked to the cluster's reactions | 4,646 rows non-empty. Merged into the file upstream on 2021-06-10 (`38f53b6957`), replacing a separate `metacyc_intermediate_rules_uniprot.tsv` (see the commented-out code at `rules.py:348-350, 390-397`) |

**Data sources.** The intermediate clusters are built from MetaCyc, KEGG **and** BRENDA reactions, not MetaCyc alone (the `Comments` prefixes above). This matches DORAnet's statement that JN3604imt "covers 87% of all common enzymatic reactions from MetaCyc, KEGG, and BRENDA" ([§4.1](https://pmc.ncbi.nlm.nih.gov/articles/PMC12512011/)).

**Naming caveat.** The numbering behind the intermediate names differs from the numbering of the 1,224-rule file, so some names point to the wrong generalized rule:

- **Where it breaks.** Prefixes up to `rule0994` always equal the true parent. From `rule0999` onward, 306 rows carry a different number: 199 have numbers above 1224 (max `rule2314`), and 107 share a name with an unrelated generalized rule. Examples: `rule1071_*` are children of generalized `rule1021`, and `rule1260` is generalized `rule1081` (computed by matching the stripped SMARTS + Reactants + Products).
- **Upstream mapping file.** The historical upstream mapping file uses the same old numbering (up to `rule2314`), and all 73,944 resolvable member reactions sit under the same prefix there.
- **Likely origin.** **[INFERENCE]** The numbers probably come from the 2,318-rule "pruned" stage of Ni 2021, before the final 1,224 rules were renumbered.
- **DORAnet renumbered.** In DORAnet's JN3604IMT the same SMARTS carry corrected parent prefixes. For example, the rule named `rule1071_2` here is `rule1021_1` there.

### Sibling files

| File | Content | Used by code? |
|---|---|---|
| `metacyc_generalized_rules.tsv` | JN1224min: `Name, Reactants, SMARTS, Products, Comments`. `Comments` holds UniProt IDs (358 rows empty), matching Pickaxe's description of JN1224min ([Pickaxe, "Reaction rules"](https://pmc.ncbi.nlm.nih.gov/articles/PMC10031857/): "includes a list of UniProt IDs for each rule") | Yes: `rules.py:102`, `README.md:35,73` |
| `metacyc21_coverage.tsv` | `Reactions, Rules`: 18,357 MetaCyc v21 reaction directions (9,185 of them `_reverse`) → one generalized rule each. 1,216 distinct rules; 8 generalized rules never appear | Yes: CDF for `metacyc_generalized` (`rules.py:101-111`). Added upstream 2021-11-30 (`2e311c1b3a`, Jon Strutz) |
| `metacyc_mapped.tsv` | A single `rule` column, 75,626 rows `ruleNNNN_k` (*k* = reaction index within an old-numbered rule, max `rule2314`). It does **not** list intermediate rule names. Some strings coincide with intermediate names (4,271), but the suffix semantics differ | **No** references in code (grep). Until `2e311c1b3a` it fed the generalized CDF. At upstream `041c58cde0` it had 4 columns: rule, source reaction ID, reaction SMILES, atom-mapped SMILES. `38f53b6957` cut it down to the rule column |
| `metacyc_coreactants.tsv` | 45 cofactor definitions (`#ID, Name, SMILES`; the last line has no trailing newline, so `wc -l` reports 45 including the header). Shared by both rule sets; `test_rules.py` expects `len(pk.coreactants) == 45` | Yes |

The historical 4-column mapping, retrieved from `raw.githubusercontent.com/tyo-nu/MINE-Database/041c58cde0/...`, has 75,626 reactions: 46,388 BRENDA, 18,178 MetaCyc and 11,060 KEGG, spread over 1,221 parents.

- **Docs discrepancy.** `docs/inputs.rst:51-52` says the rules condense "approximately 70,000 MetaCyc reactions". The data shows about 75k reactions, most of them from BRENDA and KEGG.
- **Coverage-table discrepancy.** The coverage table in `docs/inputs.rst:55-70` (272 rules → 90%) matches the CDF cutoffs in the deleted notebook (`axvline` at 272/500/955), which was built on this cross-database mapping. The current MetaCyc-only CDF gives 413 rules at 0.9 (`tests/test_unit/test_rules.py:50`, reproduced below). Pickaxe reports 353 rules for 90% ([Pickaxe, "Reaction rules"](https://pmc.ncbi.nlm.nih.gov/articles/PMC10031857/)).

## 3. How the repo uses the intermediate rules

- **`mine_database/rules.py:287-440` — `metacyc_intermediate(n_rules, fraction_coverage, anaerobic, include_containing, exclude_containing)`:**
  1. It loads the TSV and sets `total_rxns = rule_df.counts.sum()` (lines 347-356).
  2. It calls `metacyc_generalized(fraction_coverage=1, …filters…, return_counts=True)` and keeps intermediate rows whose `Name` contains any surviving generalized name (regex `"|".join(names)`, lines 359-373). So anaerobic/include/exclude filtering is applied to the **parent generalized** SMARTS, not to the intermediate SMARTS.
  3. It sorts by intermediate `counts` and computes `cdf = cumsum(counts) / total_rxns` (lines 387-388). Then:
     - `n_rules` takes the top *n*;
     - `fraction_coverage` takes `bisect_right(cdf, f) + 1` rules;
     - otherwise all rows are returned (lines 411-425).
  4. It drops `cdf`/`counts` and returns `(StringIO rules, coreactant path, name)` (lines 431-440). `Comments` and `Uniprot` stay in the stream.
- **What `fraction_coverage` means differs between the two selectors.** For generalized rules it is the share of the **MetaCyc v21** reaction directions in `metacyc21_coverage.tsv` (`rules.py:101-111, 170`). For intermediate rules it is the share of the summed intermediate `counts`, i.e. MetaCyc+KEGG+BRENDA reactions (`rules.py:356, 388`). So `fraction_coverage=0.9` does not describe the same quantity in both functions.
- **Observed outputs.** These were obtained by running `rules.py` from this checkout, and they match the test expectations in `tests/test_unit/test_rules.py:81-132`.

  | Call | Rules returned |
  |---|---|
  | `metacyc_intermediate()` | 7,154 |
  | `metacyc_intermediate(fraction_coverage=0.2)` | 75 |
  | `metacyc_intermediate(fraction_coverage=0.9)` | 4,125 |
  | `metacyc_intermediate(n_rules=20)` | 20 |
  | `metacyc_generalized()` | 1,216 |
  | `metacyc_generalized(fraction_coverage=0.9)` | 413 |
  | `metacyc_generalized(fraction_coverage=0.2)` | 7 |

  - *Why 7,154 and not 7,358 rows:* 199 rows with prefixes above `rule1224` never match a generalized name, so 7,159 rows remain after the name filter. A further 5 rows belong to the 8 generalized rules that are absent from `metacyc21_coverage.tsv`, which leaves 7,154 (computed).
  - *Consequence of the naming caveat:* the 107 mislabelled rows with prefixes ≤ 1224 are filtered by an unrelated generalized rule's SMARTS and cofactors, and the 199 high-numbered rows are always dropped. **[INFERENCE]** This silently loses about 2.7% of the intermediate rules and can skew `include_containing`/`exclude_containing` for those rows.
- **Loading (`mine_database/pickaxe.py:377-437`).** Every TSV column is loaded into the operator dict. Only `Name`, `Reactants`, `Products` and `SMARTS` are interpreted. The rule is compiled with RDKit `ReactionFromSmarts`, and the template count must equal the number of `Reactants`/`Products` slots.
- **CLI (`mine_database/pickaxe_commons.py`).**
  - It imports both selectors at line 43.
  - `--metacyc_rules {general,intermediate}` together with `--rule_coverage` or `--rule_count` selects the subset (lines 1508-1563).
  - It refuses a run if `--rule_list` and `--metacyc_rules` are both given (lines 1531-1532).
- **Examples and docs.**
  - `Scripts/example_expansion.py:42` uses `metacyc_intermediate(fraction_coverage=0.2)`.
  - `docs/inputs.rst:72-74` says intermediate operators "are less generalized than the generalized ruleset and provide uniprot information for each operator". `docs/inputs.rst:112-120` gives an include/exclude example.
  - `docs/_static/files/pickaxe_run.py:27` imports `metacyc_intermediate_uniprot`, but `rules.py` does not define it (stale). It existed upstream at `20e62da8f1` (2021-03-16) and was gone by `98f00138ca` (2021-05-06). That commit's `rules.py` defines only `metacyc_intermediate` (checked with grep on the raw file).
- **This fork's production runs.** The LOTUS runs in this fork use generalized rules: `README.md:35,73` and `scripts_of_commonslab/pickaxe_lotus.sh:41-42` pass `metacyc_generalized_rules.tsv` via `--rule_list`. An earlier lab note reached the same conclusion ([commons-dws-public, pamrein 2024-04-16](https://github.com/commons-research/commons-dws-public/blob/main/vault/open-notebook.commons.pamrein.2024.04.16.md): "the loaded rules in pickaxe is the generalized_rules").

## 4. Provenance

### Upstream history (`tyo-nu/MINE-Database`, via the GitHub API)

| Date | Commit | Author | Change |
|---|---|---|---|
| 2021-01-22 | `041c58cde0` | Kevin Shebek | "restructure, fix filters, fix cofactor redundancy": adds `metacyc_generalized_rules.tsv` and the 4-column `metacyc_mapped.tsv` |
| 2021-03-16 | `20e62da8f1` | Kevin Shebek | "add tests for rules.py": **adds `metacyc_intermediate_rules.tsv`** (7,328 rules, no `counts`/`Uniprot`), `metacyc_intermediate_rules_uniprot.tsv`, and `rules.py` with `metacyc_intermediate` + `metacyc_intermediate_uniprot` |
| 2021-05-06 | `98f00138ca` | Kevin Shebek | "Update rule selection and uniprot annotation" |
| 2021-06-10 | `38f53b6957` | Kevin Shebek | "Remove unecessary files": rewrites the intermediate TSV to the current 7,358 rows (+`counts`, +`Uniprot`), deletes the uniprot TSV and the selection notebook, strips `metacyc_mapped.tsv` to a single column |
| 2021-11-30 | `2e311c1b3a` | Jon Strutz | "Various bug fixes…": adds `metacyc21_coverage.tsv` and switches the generalized CDF to it |

There is no later upstream commit touching the intermediate TSV (`commits?path=…metacyc_intermediate_rules.tsv` returns only `20e62da8f1`, `38f53b6957`).

### This repo

- `git log --follow` on the file shows one commit: `aa2a4d9` (2024-04-03, pamrein, "add data folder"). The content is identical to upstream master.

### Publications

| Rule set / tool | Publication | What it says about the rules |
|---|---|---|
| JN1224min | Ni et al. 2021 ([OSTI](https://www.osti.gov/servlets/purl/1852562)) | Defines JN1224min. Intermediate rules are absent from the text (pypdf text search for "intermediate" finds no hits) |
| Pickaxe | Shebek et al. 2023 ([PMC10031857](https://pmc.ncbi.nlm.nih.gov/articles/PMC10031857/)) | Describes only JN1224min |
| MINE 2.0 | Strutz et al. 2022 ([PMC9237697](https://pmc.ncbi.nlm.nih.gov/articles/PMC9237697/)) | Uses the top 500 generalized rules |
| JN3604imt | DORAnet ([PMC12512011](https://pmc.ncbi.nlm.nih.gov/articles/PMC12512011/), §3.1 and §4.1) | Names "JN3604imt" and its "optimized intermediate specificity". DORAnet ships it as its default enzymatic rule set ([`doranet/modules/enzymatic/generate_network.py`](https://github.com/wsprague-nu/doranet/blob/main/doranet/modules/enzymatic/generate_network.py): `DEFAULT_RULESET = "JN3604IMT"`) |

### Relation to JN3604IMT (computed against DORAnet's `JN3604IMT_rules.tsv`, commit `471bb23c74`)

- Same 5-column format as the original intermediate file. Its `Comments` hold UniProt IDs, equal to this file's `Uniprot` for 95.5% of shared rules.
- 566 of its 3,604 SMARTS appear verbatim in this file.
- It contains no SMARTS identical to a generalized rule.
- **[INFERENCE]** JN3604IMT is a later, re-clustered and renumbered successor of the 2021 intermediate file. It is not a subset of it.

## 5. Open questions

1. **Exact algorithm.** The clustering criterion, how each cluster's MCS/environment is chosen, and how negative environments are assigned. These are only in Ni's 2022 thesis, which was not found online. Ask the Tyo/Broadbelt lab or obtain it via ProQuest.
2. **Why only 96% self-match.** In the RDKit check, 4% of member reactions are not matched by their own intermediate templates. Possible causes: stereo/tautomer handling (Ni 2021 §2.5 allowed tautomer enumeration when mapping), aromaticity perception, or the source reaction having been mapped in the other direction. Not resolved.
3. **Relation to "Pathway-level clustering" (Pate et al.).** Is the 3,597-template rule set in Pate et al. the same as JN3604imt? The numbers are close but not identical. Also, why does the 2021 file have about 2× more rules (7,358)? **[INFERENCE]** Possibly a stricter cluster cut-off, or BRENDA-only clusters that were later pruned.
4. **Fixing the naming caveat.** Should the repo re-key intermediate names to their true generalized parent (mapping derivable as in §2)? The alternative is to switch to DORAnet's JN3604IMT, which needs its cofactor file (`all_cofactors.tsv`) to be compatible with `metacyc_coreactants.tsv`. Not checked.
5. **Stale docs.** `docs/inputs.rst` (70,000 MetaCyc reactions; 272 rules → 90%) and `docs/_static/files/pickaxe_run.py:27` (nonexistent `metacyc_intermediate_uniprot`) are out of date relative to the code.

## Reproduction

The commands were run read-only. Temporary scripts in `/tmp` are not part of the repo.

- **Statistics:** `uv run --no-project --with pandas python` over the TSVs. This covers row counts, column fill, parent matching after stripping `;$(...)`/`;!$(...)`, uniqueness of comment IDs, and negative-vs-sibling environment equality.
- **RDKit checks:** `uv run --no-project --with pandas --with rdkit python`.
  - Selector outputs come from importing `mine_database/rules.py`.
  - Substructure checks use the historical `metacyc_mapped.tsv` from `https://raw.githubusercontent.com/tyo-nu/MINE-Database/041c58cde0/minedatabase/data/metacyc_rules/metacyc_mapped.tsv`, testing only `Any` reactant templates without kekulization (Pickaxe default `kekulize=False`, `pickaxe.py:147`).
- **Upstream history:** `api.github.com/repos/tyo-nu/MINE-Database/commits?path=…` and `/commits/<sha>`.
- **JN1224MIN / JN3604IMT:** fetched with `gh api repos/wsprague-nu/doranet/contents/doranet/modules/enzymatic/<file>`.
