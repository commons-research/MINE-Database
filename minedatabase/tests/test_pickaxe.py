import os
import re
import hashlib
import subprocess
from filecmp import cmp

from rdkit.Chem import AllChem
from minedatabase import pickaxe
from minedatabase.databases import MINE

data_dir = os.path.dirname(__file__)+'/data'


def purge(directory, pattern):
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))

pk = pickaxe.Pickaxe()
rule = None
cdrule = None
meh = 'CCC(=O)C(=O)O'
l_ala = 'C[C@H](N)C(=O)O'
d_ala = 'C[C@@H](N)C(=O)O'
fadh = 'Cc1cc2c(cc1C)N(CC(O)C(O)C(O)COP(=O)(O)OP(=O)(O)OCC1OC(n3cnc4c(N)ncnc43)C(O)C1O)c1nc(O)nc(O)c1N2'


def test_cofactor_loading():
    pk2 = pickaxe.Pickaxe(coreactant_list=data_dir + '/test_coreactants.tsv')
    assert "O=C=O" in pk2._raw_compounds
    c_id = pk2._raw_compounds['O=C=O']
    assert c_id in pk2.compounds
    assert pk2.compounds[c_id]['Type'] == 'Coreactant'
    assert isinstance(pk2.coreactants['ATP'][0], AllChem.Mol)
    assert pk2.coreactants['ATP'][1][0] == "X"


def test_reaction_rule_loading():
    global rule
    pk2 = pickaxe.Pickaxe(coreactant_list=data_dir + '/test_coreactants.tsv',
                          rule_list=data_dir + '/test_reaction_rules.tsv')
    rule = pk2.rxn_rules['2.7.1.a']
    assert isinstance(rule[0], AllChem.ChemicalReaction)
    assert isinstance(rule[1], dict)
    assert rule[1]['Reactants'] == ['ATP', 'Any']
    assert "Products" in rule[1]
    assert "Comments" in rule[1]


def test_compound_loading():
    compound_smiles = pk.load_compound_set(compound_file=data_dir+'/test_compounds.tsv')
    assert len(compound_smiles) == 14


def test_transform_compounds():
    pk._add_compound("Start", smi=fadh)
    pk._load_coreactant('ATP		Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)OP(=O)(O)O)[C@@H](O)[C@H]1O')
    pk._load_coreactant('ADP		Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)O)[C@@H](O)[C@H]1O')
    pk.rxn_rules['2.7.1.a'] = rule
    pk.transform_compound(fadh)
    pk.assign_ids()


def test_transform_compounds_implicit():
    pk2 = pickaxe.Pickaxe(explicit_h=False, kekulize=False,
                          coreactant_list=data_dir + '/test_coreactants.tsv',
                          rule_list=data_dir + '/test_cd_rxn_rule.tsv')
    pk2._add_compound("Start", smi=meh)
    pk2.transform_compound(meh)
    assert len(pk2.compounds) == 38
    assert len(pk2.reactions) == 1


def test_hashing():
    pk2 = pickaxe.Pickaxe(coreactant_list=data_dir + '/test_coreactants.tsv',
                          rule_list=data_dir + '/test_reaction_rules.tsv')
    pk2._load_coreactant('S-Adenosylmethionine		C[S+](CC[C@H](N)C(=O)O)C[C@H]1O[C@@H](n2cnc3c(N)ncnc32)[C@H](O)[C@@H]1O')
    pk2.transform_compound(l_ala)
    len_rxns = len(pk2.reactions)
    assert len_rxns
    pk2.transform_compound(d_ala)
    assert len(pk2.reactions) == 2 * len_rxns


def test_product_racimization():
    pk2 = pickaxe.Pickaxe(racemize=False, coreactant_list=data_dir + '/test_coreactants.tsv',
                          rule_list=data_dir+'/test_reaction_rules.tsv')
    comps, rxns = pk2.transform_compound(meh, rules=['2.6.1.a'])
    assert len(comps) == 38
    assert len(rxns) == 1
    pk2 = pickaxe.Pickaxe(racemize=True, coreactant_list=data_dir + '/test_coreactants.tsv',
                          rule_list=data_dir+'/test_reaction_rules.tsv')
    rcomps, rrxns = pk2.transform_compound(meh, rules=['2.6.1.a'])
    assert len(rcomps) == 39
    assert len(rrxns) == 2


def test_compound_output_writing():
    expected = hashlib.sha256(
        open(data_dir+'/testcompoundsout', 'rb').read()).hexdigest()
    pk.write_compound_output_file(data_dir+'/testcompoundsout')
    assert os.path.exists(data_dir+'/testcompoundsout_new')
    try:
        assert hashlib.sha256(open(data_dir+'/testcompoundsout_new', 'rb'
                                   ).read()).hexdigest() == expected
    finally:
        os.remove(data_dir+'/testcompoundsout_new')


def test_reaction_output_writing():
    expected = hashlib.sha256(
        open(data_dir + '/testreactionsout', 'rb').read()).hexdigest()
    pk.write_reaction_output_file(data_dir+'/testreactionsout')
    assert os.path.exists(data_dir+'/testreactionsout_new')
    try:
        assert hashlib.sha256(open(data_dir + '/testreactionsout_new', 'rb'
                                   ).read()).hexdigest() == expected
    finally:
        os.remove(data_dir+'/testreactionsout_new')


def test_transform_all():
    pk3 = pickaxe.Pickaxe(errors=False)
    pk3._load_coreactant('ATP		Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)OP(=O)(O)O)[C@@H](O)[C@H]1O')
    pk3._load_coreactant('ADP		Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)O)[C@@H](O)[C@H]1O')
    pk3._add_compound(fadh, fadh, type='Starting Compound')
    pk3.rxn_rules['2.7.1.a'] = rule
    pk3.transform_all(max_generations=2)
    assert len(pk3.compounds) == 31
    assert len(pk3.reactions) == 49
    comp_gens = set([x['Generation'] for x in pk3.compounds.values()])
    assert comp_gens == {0, 1, 2}


def test_multiprocessing(params=None):
    if params:
        pk3 = pickaxe.Pickaxe(**params)
    else:
        pk3 = pickaxe.Pickaxe()
    pk3._load_coreactant('ATP		Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)OP(=O)(O)O)[C@@H](O)[C@H]1O')
    pk3._load_coreactant('ADP		Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)O)[C@@H](O)[C@H]1O')
    pk3._add_compound(fadh, fadh, type='Starting Compound')
    pk3.rxn_rules['2.7.1.a'] = rule
    pk3.transform_all(max_generations=2, num_workers=2)
    assert len(pk3.compounds) == 31
    assert len(pk3.reactions) == 49
    comp_gens = set([x['Generation'] for x in pk3.compounds.values()])
    assert comp_gens == {0, 1, 2}
    return pk3


def test_cli():
    os.chdir(data_dir+"/../..") # ensure the following executes from minedatabase
    rc = subprocess.call('python pickaxe.py -o tests -r tests/data/test_cd_rxn_rule.tsv', shell=True)
    assert not rc
    purge('tests/', ".*\.tsv$")


def test_pruning():
    pk3 = test_multiprocessing({'database': 'MINE_test', 'image_dir':
        data_dir})
    ids = ['C9d4089d24d09c0c86a817af75ded95dd0f6d5b07', 'C177697ec7f877acf4f1439ce57c03c22fbe5f897', 'C69']
    pk3.prune_network(ids)
    pk3.assign_ids()
    pk3.write_compound_output_file(data_dir + '/pruned_comps')
    pk3.write_reaction_output_file(data_dir + '/pruned_rxns')
    assert os.path.exists(data_dir + '/pruned_comps_new')
    assert os.path.exists(data_dir + '/pruned_rxns_new')
    try:
        assert cmp(data_dir + '/pruned_comps', data_dir + '/pruned_comps_new')
    finally:
        os.remove(data_dir + '/pruned_comps_new')
    try:
        assert cmp(data_dir + '/pruned_rxns', data_dir + '/pruned_rxns_new')
    finally:
        os.remove(data_dir + '/pruned_rxns_new')


def test_load_compounds_from_MINE():
    pk2 = pickaxe.Pickaxe(database='mongotest')
    compound_smiles = pk2.load_compound_set()
    assert len(compound_smiles) == 26


def test_save_as_MINE():
    pk3 = test_multiprocessing({'database': 'MINE_test', 'image_dir':
        data_dir})
    pk3.save_to_MINE("MINE_test")
    mine_db = MINE('MINE_test')
    try:
        assert mine_db.compounds.count() == 31
        assert mine_db.reactions.count() == 49
        assert mine_db.operators.count() == 1
        assert mine_db.operators.find_one()["Reactions_predicted"] == 49
        assert os.path.exists(data_dir+'/X9c69cbeb40f083118c1913599c12c7f4e5e68d03.svg')
        start_comp = mine_db.compounds.find_one({'Type': 'Starting Compound'})
        assert len(start_comp['Reactant_in'])
        # Don't track sources of coreactants
        coreactant = mine_db.compounds.find_one({'Type': 'Coreactant'})
        assert 'Sources' not in coreactant
        product = mine_db.compounds.find_one({'Generation': 2})
        assert len(product['Product_of'])
        assert len(product['Sources'])
        assert product['Type'] == 'Predicted'
    finally:
        mine_db.compounds.drop()
        mine_db.reactions.drop()
        mine_db.operators.drop()
        purge(data_dir, ".*\.svg$")


def test_save_no_rxn_MINE():
    pk3 = pickaxe.Pickaxe(database='MINE_test')
    pk3.load_compound_set(compound_file=data_dir + '/test_compounds.tsv')
    pk3.save_to_MINE("MINE_test")
    mine_db = MINE('MINE_test')
    try:
        assert mine_db.compounds.count() == 14
        assert mine_db.reactions.count() == 0
    finally:
        mine_db.compounds.drop()
        mine_db.reactions.drop()
        mine_db.operators.drop()