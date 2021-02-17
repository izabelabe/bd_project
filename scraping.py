import requests
from PIL import Image
from bs4 import BeautifulSoup
import re
import pubchempy as pcb
import os

def parse_product(bcode: str):
    url = 'https://world.openfoodfacts.org/product/' + bcode
    res = requests.get(url)
    e_pattern = "[a-zA-Z][0-9]{3}[a-zA-Z]?"
    try:
        res.raise_for_status()

        product_soup = BeautifulSoup(res.text, 'html.parser')
        barcode = bcode

        product_name = product_soup.title.string

        producer_tag = product_soup.find(itemprop="brand")
        producer = None
        if producer_tag is not None:
            producer = producer_tag.text

        ingredients = product_soup.find(id="ingredients_list")
        if ingredients is not None:
            ingredients = ingredients.text

        adds_list = product_soup.find(style="display:block;float:left;")
        adds = []
        if adds_list != None:
            adds = [item.text for item in adds_list.contents if item.name == 'li']
            adds = [re.findall(e_pattern, item)[0] for item in adds if len(re.findall(e_pattern, item)) != 0]
            # pubchem_adds = get_adds(adds)

        nutrition_table = product_soup.find(id="nutrition_data_table")
        kcal = None
        if nutrition_table is not None:
            kcal = nutrition_table.find(id="nutriment_energy-kcal_tr")
            if kcal is not None:
                kcal = kcal.contents[3].text.replace('\t', '').replace('\n', '')
                if kcal == '?':
                    return None
            else:
                return None

        fat_tag = nutrition_table.find(id="nutriment_fat_tr")
        if fat_tag is not None:
            fat = fat_tag.contents[3].text.replace('\t', '').replace('\n', '')
            if kcal == '?':
                return None
        else:
            return None

        saturated_fat_tag = nutrition_table.find(id="nutriment_saturated-fat_tr")
        if saturated_fat_tag is not None:
            saturated_fat = saturated_fat_tag.contents[3].text.replace('\t', '').replace('\n', '')
            if kcal == '?':
                return None
        else:
            return None

        carbs_tag = nutrition_table.find(id="nutriment_carbohydrates_tr")
        if carbs_tag is not None:
            carbs = carbs_tag.contents[3].text.replace('\t', '').replace('\n', '')
            if kcal == '?':
                return None
        else:
            return None

        sugar_tag = nutrition_table.find(id="nutriment_sugars_tr")
        if sugar_tag is not None:
            sugar = sugar_tag.contents[3].text.replace('\t', '').replace('\n', '')
            if kcal == '?':
                return None
        else:
            return None

        protein_tag = nutrition_table.find(id="nutriment_proteins_tr")
        if protein_tag is not None:
            protein = protein_tag.contents[3].text.replace('\t', '').replace('\n', '')
            if kcal == '?':
                return None
        else:
            return None

        salt_tag = nutrition_table.find(id="nutriment_salt_tr")
        if salt_tag is not None:
            salt = salt_tag.contents[3].text.replace('\t', '').replace('\n', '')
            if salt == '?':
                return None
        else:
            return None

        img_source = product_soup.find(id="og_image")
        im = None
        if img_source is not None:
            im = Image.open(requests.get(img_source['src'], stream=True).raw)


        nutri_score_tag = product_soup.find_all(title="How the color nutrition grade is computed")
        nutri_score = None
        if nutri_score_tag is not None:
            if len(nutri_score_tag) != 0:
                nutri_score_tag = nutri_score_tag[1].contents[0]
                nutri_score = nutri_score_tag['alt'][-1:]


        # if im is not None:
        #     display(im)

        cwd = os.getcwd()
        print(cwd)


        return {'barcode': barcode,
                'product_name': product_name,
                'producer': producer,
                'ingredients': ingredients,
                'adds': adds,
                'kcal': kcal,
                'fat': fat,
                'saturated_fat': saturated_fat,
                'carbs': carbs,
                'sugar': sugar,
                'protein': protein,
                'salt': salt,
                'im': im,
                'nutri_score': nutri_score}


    except requests.HTTPError as err:
        # print(err)
        return None


def get_pubchem_adds(adds: list):
    results = []
    for add in adds:
        res = {}
        comps = pcb.get_compounds(add, 'name')
        if len(comps) != 0:
            res['cid'] = comps[0].cid
            res['name'] = add
            if len(comps[0].synonyms) >3:
                res['synonyms'] = ', '.join(comps[0].synonyms[:3])
            else:
                res['synonyms'] = ', '.join(comps[0].synonyms)
            res['molecular_formula'] = comps[0].molecular_formula
            res['molecular_weight'] = comps[0].molecular_weight
            res['canonical_smiles'] = comps[0].canonical_smiles



            results.append(res)

    return results

if __name__ == '__main__':
    main_url = 'https://world.openfoodfacts.org/product/'
    barcode = '5449000000996'
    barcode = ''
    max_val = 9999999999999
    val = 3
    while val < max_val:
        barcode = str(val)
        res = parse_product((13 - len(barcode)) * '0' + barcode)

        val = val + 1

    items = parse_product(barcode)
    print(items['adds'])
    print(items['im'])
    adds = get_pubchem_adds(items['adds'])
    print(adds)

