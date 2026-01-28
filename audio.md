
## Voice

It's possible to include automatic narration. Could be helpful for the visually impaired.

### Coqui TTS

Requires Python 3.10 or 3.11 (not 3.12 or higher)


```
# 1. Create a 3.10 virtual env (via pyenv or brew)
brew install pyenv
brew install pyenv-virtualenv

pyenv install 3.10.14
pyenv virtualenv 3.10.14 coqui-tts
pyenv activate coqui-tts

# 2. Now install
pip install coqui-tts

# 3. Try it out
tts --text "Zeta-5 hums in the reactor core" --model_name tts_models/en/vctk/vits --out_path out.wav
```

#### available models

```tts_models/en/vctk/vits```
```tts_models/multilingual/multi-dataset/xtts_v2```
```tts_models/en/ljspeech/vits```
```tts_models/en/ljspeech/tacotron2-DDC```
```tts_models/en/ljspeech/glow-tts```


#### available voices

```
# list available speakers for this model
tts --model_name tts_models/en/vctk/vits --list_speaker_idxs
...
 > Available speaker ids: (Set --speaker_idx flag to one of these values to use the multi-speaker model.
{'ED\n': 0, 'p225': 1, 'p226': 2, 'p227': 3, 'p228': 4, 'p229': 5, 'p230': 6, 'p231': 7, 'p232': 8, 'p233': 9, 'p234': 10, 'p236': 11, 'p237': 12, 'p238': 13, 'p239': 14, 'p240': 15, 'p241': 16, 'p243': 17, 'p244': 18, 'p245': 19, 'p246': 20, 'p247': 21, 'p248': 22, 'p249': 23, 'p250': 24, 'p251': 25, 'p252': 26, 'p253': 27, 'p254': 28, 'p255': 29, 'p256': 30, 'p257': 31, 'p258': 32, 'p259': 33, 'p260': 34, 'p261': 35, 'p262': 36, 'p263': 37, 'p264': 38, 'p265': 39, 'p266': 40, 'p267': 41, 'p268': 42, 'p269': 43, 'p270': 44, 'p271': 45, 'p272': 46, 'p273': 47, 'p274': 48, 'p275': 49, 'p276': 50, 'p277': 51, 'p278': 52, 'p279': 53, 'p280': 54, 'p281': 55, 'p282': 56, 'p283': 57, 'p284': 58, 'p285': 59, 'p286': 60, 'p287': 61, 'p288': 62, 'p292': 63, 'p293': 64, 'p294': 65, 'p295': 66, 'p297': 67, 'p298': 68, 'p299': 69, 'p300': 70, 'p301': 71, 'p302': 72, 'p303': 73, 'p304': 74, 'p305': 75, 'p306': 76, 'p307': 77, 'p308': 78, 'p310': 79, 'p311': 80, 'p312': 81, 'p313': 82, 'p314': 83, 'p316': 84, 'p317': 85, 'p318': 86, 'p323': 87, 'p326': 88, 'p329': 89, 'p330': 90, 'p333': 91, 'p334': 92, 'p335': 93, 'p336': 94, 'p339': 95, 'p340': 96, 'p341': 97, 'p343': 98, 'p345': 99, 'p347': 100, 'p351': 101, 'p360': 102, 'p361': 103, 'p362': 104, 'p363': 105, 'p364': 106, 'p374': 107, 'p376': 108}
```

```
# synthesize voice with a chosen speaker
tts --text "Zeta-5 hums in the reactor core" \
    --model_name tts_models/en/vctk/vits \
    --speaker_idx p225 \
    --out_path out.wav
```

#### voice samples

##### male

###### tts_models/multilingual/multi-dataset/xtts_v2

Royston Min
<audio controls>
    <source src="./audio/Royston_Min.wav" type="audio/wav">
</audio>

Viktor Eka (gravelly)
<audio controls>
    <source src="./audio/Viktor_Eka.wav" type="audio/wav">
</audio>

Abrahan Mack
<audio controls>
    <source src="./audio/Abraham_Mack.wav" type="audio/wav">
</audio>

Adde Michal
<audio controls>
    <source src="./audio/Adde_Michal.wav" type="audio/wav">
</audio>

Baldur Sanjin
<audio controls>
    <source src="./audio/Baldur_Sanjin.wav" type="audio/wav">
</audio>

Damien Black
<audio controls>
    <source src="./audio/Damien_Black.wav" type="audio/wav">
</audio>

Gilberto Mathias
<audio controls>
    <source src="./audio/Gilberto_Mathias.wav" type="audio/wav">
</audio>

Ilkin Urbano
<audio controls>
    <source src="./audio/Ilkin_Urbano.wav" type="audio/wav">
</audio>

Kazuhiko Atallah
<audio controls>
    <source src="./audio/Kazuhiko_Atallah.wav" type="audio/wav">
</audio>

Ludvig Milivoj
<audio controls>
    <source src="./audio/Ludvig_Milivoj.wav" type="audio/wav">
</audio>

Torcull Diarmuid
<audio controls>
    <source src="./audio/Torcull_Diarmuid.wav" type="audio/wav">
</audio>

Viktor Menelaos
<audio controls>
    <source src="./audio/Viktor_Menelaos.wav" type="audio/wav">
</audio>

Zacharie Aimilios
<audio controls>
    <source src="./audio/Zacharie_Aimilios.wav" type="audio/wav">
</audio>

Nova Hogarth
<audio controls>
    <source src="./audio/Nova_Hogarth.wav" type="audio/wav">
</audio>

Eugenio Mataracı (heavy sigh guy)
<audio controls>
    <source src="./audio/Eugenio_Mataraci.wav" type="audio/wav">
</audio>

Ferran Simen
<audio controls>
    <source src="./audio/Ferran_Simen.wav" type="audio/wav">
</audio>

Xavier Hayasaka (plodding pausing narration)
<audio controls>
    <source src="./audio/Xavier_Hayasaka.wav" type="audio/wav">
</audio>

Luis Moray (nerdy matter-of-fact narration) (may introduce nonsense words)
<audio controls>
    <source src="./audio/Luis_Moray.wav" type="audio/wav">
</audio>

Marcos Rudaski
<audio controls>
    <source src="./audio/Marcos_Rudaski.wav" type="audio/wav">
</audio>

Ige Behringer (decent narration) (interjects chinese language randomly)
<audio controls>
    <source src="./audio/Ige_Behringer.wav" type="audio/wav">
</audio>

Filip Traverse (good gentle narration)
<audio controls>
    <source src="./audio/Filip_Traverse.wav" type="audio/wav">
</audio>

Damjan Chapman (elder nerd - apt articulate narration)
<audio controls>
    <source src="./audio/Damjan_Chapman.wav" type="audio/wav">
</audio>

Wulf Carlevaro (excellent diction and narration)
<audio controls>
    <source src="./audio/Wulf_Carlevaro.wav" type="audio/wav">
</audio>

Aaron Dreschner (good narrator)
<audio controls>
    <source src="./audio/Aaron_Dreschner.wav" type="audio/wav">
</audio>

Kumar Dahl (good narration - gentle bedroom voice)
<audio controls>
    <source src="./audio/Kumar_Dahl.wav" type="audio/wav">
</audio>

###### tts_models/en/vctk/vits
p228
<audio controls>
    <source src="./audio/228.wav" type="audio/wav">
</audio>

p229
<audio controls>
    <source src="./audio/229.wav" type="audio/wav">
</audio>

p230
<audio controls>
    <source src="./audio/230.wav" type="audio/wav">
</audio>

p231
<audio controls>
    <source src="./audio/231.wav" type="audio/wav">
</audio>

p232
<audio controls>
    <source src="./audio/232.wav" type="audio/wav">
</audio>

p233 (India/Pakistani accent)
<audio controls>
    <source src="./audio/233.wav" type="audio/wav">
</audio>

p234
<audio controls>
    <source src="./audio/234.wav" type="audio/wav">
</audio>

p236
<audio controls>
    <source src="./audio/236.wav" type="audio/wav">
</audio>

p238
<audio controls>
    <source src="./audio/238.wav" type="audio/wav">
</audio>

p239
<audio controls>
    <source src="./audio/239.wav" type="audio/wav">
</audio>

p241
<audio controls>
    <source src="./audio/241.wav" type="audio/wav">
</audio>

p251
<audio controls>
    <source src="./audio/251.wav" type="audio/wav">
</audio>

p252
<audio controls>
    <source src="./audio/252.wav" type="audio/wav">
</audio>

p253
<audio controls>
    <source src="./audio/253.wav" type="audio/wav">
</audio>

p255 🌟?
<audio controls>
    <source src="./audio/255.wav" type="audio/wav">
</audio>

p256
<audio controls>
    <source src="./audio/256.wav" type="audio/wav">
</audio>

p258
<audio controls>
    <source src="./audio/258.wav" type="audio/wav">
</audio>

p262
<audio controls>
    <source src="./audio/262.wav" type="audio/wav">
</audio>

p264
<audio controls>
    <source src="./audio/264.wav" type="audio/wav">
</audio>

p265
<audio controls>
    <source src="./audio/265.wav" type="audio/wav">
</audio>

p267
<audio controls>
    <source src="./audio/267.wav" type="audio/wav">
</audio>

p269
<audio controls>
    <source src="./audio/269.wav" type="audio/wav">
</audio>

p272
<audio controls>
    <source src="./audio/272.wav" type="audio/wav">
</audio>

p279
<audio controls>
    <source src="./audio/279.wav" type="audio/wav">
</audio>

p281
<audio controls>
    <source src="./audio/281.wav" type="audio/wav">
</audio>

p282
<audio controls>
    <source src="./audio/282.wav" type="audio/wav">
</audio>

p285
<audio controls>
    <source src="./audio/285.wav" type="audio/wav">
</audio>

p286
<audio controls>
    <source src="./audio/286.wav" type="audio/wav">
</audio>

p287 (deep)
<audio controls>
    <source src="./audio/287.wav" type="audio/wav">
</audio>

p289
<audio controls>
    <source src="./audio/289.wav" type="audio/wav">
</audio>

p301
<audio controls>
    <source src="./audio/301.wav" type="audio/wav">
</audio>

p302
<audio controls>
    <source src="./audio/302.wav" type="audio/wav">
</audio>

p307
<audio controls>
    <source src="./audio/307.wav" type="audio/wav">
</audio>

p312
<audio controls>
    <source src="./audio/312.wav" type="audio/wav">
</audio>

p313
<audio controls>
    <source src="./audio/313.wav" type="audio/wav">
</audio>

p317
<audio controls>
    <source src="./audio/317.wav" type="audio/wav">
</audio>

p318
<audio controls>
    <source src="./audio/318.wav" type="audio/wav">
</audio>

p326
<audio controls>
    <source src="./audio/326.wav" type="audio/wav">
</audio>

p330
<audio controls>
    <source src="./audio/330.wav" type="audio/wav">
</audio>

p340
<audio controls>
    <source src="./audio/340.wav" type="audio/wav">
</audio>

p376 (gravelly/vocal fry)
<audio controls>
    <source src="./audio/376.wav" type="audio/wav">
</audio>


## FEMALE
##### FEMALE

###### tts_models/multilingual/multi-dataset/xtts_v2


Claribel Dervla
<audio controls>
    <source src="./audio/Claribel_Dervla.wav" type="audio/wav">
</audio>

Daisy Studious
<audio controls>
    <source src="./audio/Daisy_Studious.wav" type="audio/wav">
</audio>

Gracie Wise
<audio controls>
    <source src="./audio/Gracie_Wise.wav" type="audio/wav">
</audio>

Tammie Ema
<audio controls>
    <source src="./audio/Tammie_Ema.wav" type="audio/wav">
</audio>

Alison Dietlinde
<audio controls>
    <source src="./audio/Alison_Dietlinde.wav" type="audio/wav">
</audio>

Ana Florence
<audio controls>
    <source src="./audio/Ana_Florence.wav" type="audio/wav">
</audio>

Annmarie Nele
<audio controls>
    <source src="./audio/Annamarie_Nele.wav" type="audio/wav">
</audio>

Badr Odhiambo
<audio controls>
    <source src="./audio/Badr_Odhiambo.wav" type="audio/wav">
</audio>

Brenda Stern
<audio controls>
    <source src="./audio/Brenda_Stern.wav" type="audio/wav">
</audio>

Gitta Nikolina
<audio controls>
    <source src="./audio/Gitta_Nikolina.wav" type="audio/wav">
</audio>

Henriette Usha
<audio controls>
    <source src="./audio/Henriette_Usha.wav" type="audio/wav">
</audio>

Sofia Hellen
<audio controls>
    <source src="./audio/Sofia_Hellen.wav" type="audio/wav">
</audio>

Tammy Grit
<audio controls>
    <source src="./audio/Tammy_Grit.wav" type="audio/wav">
</audio>

Tanja Adelina
<audio controls>
    <source src="./audio/Tanja_Adelina.wav" type="audio/wav">
</audio>

Vjollca Johnnie
<audio controls>
    <source src="./audio/Vjollca_Johnnie.wav" type="audio/wav">
</audio>

Nova Hogarth
<audio controls>
    <source src="./audio/Nova_Hogarth.wav" type="audio/wav">
</audio>

Maja Ruoho
<audio controls>
    <source src="./audio/Maja_Ruoho.wav" type="audio/wav">
</audio>

Lidiya Szekeres
<audio controls>
    <source src="./audio/Lidiya_Szekeres.wav" type="audio/wav">
</audio>

Chandra MacFarland
<audio controls>
    <source src="./audio/Chandra_MacFarland.wav" type="audio/wav">
</audio>

Szofi Granger (good narration)
<audio controls>
    <source src="./audio/Szofi_Granger.wav" type="audio/wav">
</audio>

Camilla Holmström
<audio controls>
    <source src="./audio/Camilla_Holmström.wav" type="audio/wav">
</audio>

Lilya Stainthorpe (nerdy quirky female narrator)
<audio controls>
    <source src="./audio/Lilya_Stainthorpe.wav" type="audio/wav">
</audio>

Zofija Kendrick (20 something college educated female narrator)
<audio controls>
    <source src="./audio/Zofija_Kendrick.wav" type="audio/wav">
</audio>

Narelle Moon (poor pronunciation)
<audio controls>
    <source src="./audio/Narelle_Moon.wav" type="audio/wav">
</audio>

Barbora MacLean
<audio controls>
    <source src="./audio/Barbora_MacLean.wav" type="audio/wav">
</audio>

Alexandra Hisakawa
<audio controls>
    <source src="./audio/Alexandra_Hisakawa.wav" type="audio/wav">
</audio>

Alma María (tendency to emit chinese sounding nonsense words)
<audio controls>
    <source src="./audio/Alma_María.wav" type="audio/wav">
</audio>

Rosemary Okafor (child-like) (tends to introduce non-sequitur sounds)
<audio controls>
    <source src="./audio/Rosemary_Okafor.wav" type="audio/wav">
</audio>

Suad Qasim

###### tts_models/en/vctk/vits

p225
<audio controls>
    <source src="./audio/225.wav" type="audio/wav">
</audio>

p227
<audio controls>
    <source src="./audio/227.wav" type="audio/wav">
</audio>

p237
<audio controls>
    <source src="./audio/237.wav" type="audio/wav">
</audio>

p240
<audio controls>
    <source src="./audio/240.wav" type="audio/wav">
</audio>

p243
<audio controls>
    <source src="./audio/243.wav" type="audio/wav">
</audio>

p244
<audio controls>
    <source src="./audio/244.wav" type="audio/wav">
</audio>

p245
<audio controls>
    <source src="./audio/245.wav" type="audio/wav">
</audio>

p246
<audio controls>
    <source src="./audio/246.wav" type="audio/wav">
</audio>

p247
<audio controls>
    <source src="./audio/247.wav" type="audio/wav">
</audio>

p248
<audio controls>
    <source src="./audio/248.wav" type="audio/wav">
</audio>

p249
<audio controls>
    <source src="./audio/249.wav" type="audio/wav">
</audio>

p250
<audio controls>
    <source src="./audio/250.wav" type="audio/wav">
</audio>

p254
<audio controls>
    <source src="./audio/254.wav" type="audio/wav">
</audio>

p257
<audio controls>
    <source src="./audio/257.wav" type="audio/wav">
</audio>

p259
<audio controls>
    <source src="./audio/259.wav" type="audio/wav">
</audio>

p260
<audio controls>
    <source src="./audio/260.wav" type="audio/wav">
</audio>

p261
<audio controls>
    <source src="./audio/261.wav" type="audio/wav">
</audio>

p263
<audio controls>
    <source src="./audio/263.wav" type="audio/wav">
</audio>

p268
<audio controls>
    <source src="./audio/263.wav" type="audio/wav">
</audio>

p271
<audio controls>
    <source src="./audio/271.wav" type="audio/wav">
</audio>

p273
<audio controls>
    <source src="./audio/273.wav" type="audio/wav">
</audio>

p274
<audio controls>
    <source src="./audio/274.wav" type="audio/wav">
</audio>

p275
<audio controls>
    <source src="./audio/275.wav" type="audio/wav">
</audio>

p276
<audio controls>
    <source src="./audio/276.wav" type="audio/wav">
</audio>

p277
<audio controls>
    <source src="./audio/277.wav" type="audio/wav">
</audio>

p278
<audio controls>
    <source src="./audio/278.wav" type="audio/wav">
</audio>

p280 (vocal fry)
<audio controls>
    <source src="./audio/280.wav" type="audio/wav">
</audio>

p283
<audio controls>
    <source src="./audio/283.wav" type="audio/wav">
</audio>

p284
<audio controls>
    <source src="./audio/284.wav" type="audio/wav">
</audio>

p288
<audio controls>
    <source src="./audio/288.wav" type="audio/wav">
</audio>

p300
<audio controls>
    <source src="./audio/300.wav" type="audio/wav">
</audio>

p303
<audio controls>
    <source src="./audio/303.wav" type="audio/wav">
</audio>

p304
<audio controls>
    <source src="./audio/304.wav" type="audio/wav">
</audio>

p305
<audio controls>
    <source src="./audio/305.wav" type="audio/wav">
</audio>

p306
<audio controls>
    <source src="./audio/306.wav" type="audio/wav">
</audio>

p308
<audio controls>
    <source src="./audio/308.wav" type="audio/wav">
</audio>

p310
<audio controls>
    <source src="./audio/310.wav" type="audio/wav">
</audio>

p311 (vocal fry)
<audio controls>
    <source src="./audio/311.wav" type="audio/wav">
</audio>

p314
<audio controls>
    <source src="./audio/314.wav" type="audio/wav">
</audio>

p316
<audio controls>
    <source src="./audio/316.wav" type="audio/wav">
</audio>

p323
<audio controls>
    <source src="./audio/316.wav" type="audio/wav">
</audio>

p329
<audio controls>
    <source src="./audio/329.wav" type="audio/wav">
</audio>

p333
<audio controls>
    <source src="./audio/333.wav" type="audio/wav">
</audio>

p334
<audio controls>
    <source src="./audio/334.wav" type="audio/wav">
</audio>

p335
<audio controls>
    <source src="./audio/335.wav" type="audio/wav">
</audio>

p336
<audio controls>
    <source src="./audio/336.wav" type="audio/wav">
</audio>

p339
<audio controls>
    <source src="./audio/339.wav" type="audio/wav">
</audio>

p341
<audio controls>
    <source src="./audio/341.wav" type="audio/wav">
</audio>

p343
<audio controls>
    <source src="./audio/343.wav" type="audio/wav">
</audio>

p345 (India/Pakistani accent)
<audio controls>
    <source src="./audio/345.wav" type="audio/wav">
</audio>

p347
<audio controls>
    <source src="./audio/347.wav" type="audio/wav">
</audio>

p351 (gender neutral)
<audio controls>
    <source src="./audio/351.wav" type="audio/wav">
</audio>

p360
<audio controls>
    <source src="./audio/360.wav" type="audio/wav">
</audio>

p361
<audio controls>
    <source src="./audio/361.wav" type="audio/wav">
</audio>

p362 (vocal fry)
<audio controls>
    <source src="./audio/362.wav" type="audio/wav">
</audio>

p363
<audio controls>
    <source src="./audio/363.wav" type="audio/wav">
</audio>

p364
<audio controls>
    <source src="./audio/364.wav" type="audio/wav">
</audio>

p374
<audio controls>
    <source src="./audio/374.wav" type="audio/wav">
</audio>

##### Child

Andrew Chipper
<audio controls>
    <source src="./audio/Andrew_Chipper.wav" type="audio/wav">
</audio>

