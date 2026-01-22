#%%
import pandas as pd
import json
from tqdm import tqdm
import re
from pathlib import Path
from itertools import chain
def keep_only_alphabets(text) -> str:
    # Regex pattern to match alphabets
    pattern = r'[a-zA-Z]'

    # Replace all characters that don't match the pattern with an empty string
    cleaned_text = re.sub(pattern=r'[^' + pattern + ']', repl='', string=text, flags=re.IGNORECASE)

    return cleaned_text
# %%

sentence_files = list(Path("../data/pdf_sentences").iterdir())
# %%

sentences = pd.concat([pd.read_parquet(f) for f in sentence_files], ignore_index=True)
# %%
headings = []
strings = []
for i, (IMRO, plan_string) in tqdm(iterable=enumerate(iterable=data.items())):
    if plan_string == []:
        continue
    headings += [plan_string[0]["heading"]]
    strings += keep_only_alphabets(text=plan_string[0]["text"].replace("\n", "").replace(".","")).lower().split(sep=" ")
# %%
j = 320
pd.Series(data=strings).value_counts().iloc[j:j+40]
# %%
{    
    "municipality":  6960,
    "agreement":  3143,
    "destination":  2957,
    "municipal":  2424,
    "feasibility":  2058,
    "exploitation":  1950,
    "obligation":  1863,
    "initiator":  1428,
    "private":  1223,
    "participation":  1208,
    "preparation": 1051,
    "feasible": 1033,
    "natura": 915,
}
# %%
sentence_set = set(sentences["sents"].str.lower().to_list())
# %%
sentence_set
# %%
sentence_set = [keep_only_alphabets(text=s.replace("\n", "").replace(".","")).lower().split(sep=" ") for s in sentence_set]
# %%
sent_df = pd.DataFrame({"words": list(chain(*sentence_set))})
# %%
sent_df.words.value_counts().head(1000).to_csv("high_count_words")
# %%
plangebied,115102
bestemmingsplan,81473
woningen,89324
ontwikkeling,52002
opgenomen,44542
ontwikkelingen,17465
provincie,16973
beleid,16936
bedrijven,15736
besluit,15682
gerealiseerd,15404
toegestaan,14207
behoeve,12565
toepassing,12083
ordening,11976
structuurvisie,11733
realisatie,11729
gebieden,11414
bouwvlak,11267
gebouwen,11139
voorgenomen,11087
goed,10213
eigen,10181
bedrijf,10159
aanduiding,9866
bouw,9603
verbeelding,9104
gemeentelijke,8808
woningbouw,8163
nieuwbouw,7658
initiatief,7549
inrichting,6764
werkzaamheden,6637
municipal council,6425
grondgebonden,5950
percelen,5916
wijzigingsplan,5870
werking,5840
aangetroffen,5793
structuur,5720
uitvoering,5109
uitbreiding,5006
planvoornemen,4852
mogelijkheid,4827
uitvoerbaarheid,4786
herontwikkeling,4568
provinciaal,4352
economische,4350
omgevingsverordening,3985
aanleg,3978
woongebied,3766
uitvoeren,3692
wethouders,3433
woonbestemming,3340
ontheffing,3306
bouwregels,3154
kosten,3149
uitwerkingsplan,3111
uitgesloten,3015
uitzondering,3009
woonwijk,2951
bijdrage,2895
verontreiniging,2859
woningbouwprogramma,2827
