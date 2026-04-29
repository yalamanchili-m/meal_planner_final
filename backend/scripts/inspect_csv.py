import pandas as pd
from pathlib import Path
path = Path('data/recipes.csv')
print('exists', path.exists())
reader = pd.read_csv(path, nrows=1)
print('columns:', list(reader.columns))
row = reader.iloc[0]
for col in ['RecipeId','Name','CookTime','PrepTime','TotalTime','Calories','RecipeIngredientQuantities','RecipeIngredientParts','RecipeInstructions','RecipeYield','RecipeServings','RecipeCategory','Keywords']:
    if col in row.index:
        print(f'\n{col}: {type(row[col]).__name__}')
        print(repr(str(row[col])[:500]))
