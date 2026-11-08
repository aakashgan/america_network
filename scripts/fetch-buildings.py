import datetime, json, pathlib, shutil, site, subprocess, sysconfig, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'data/buildings/raw/overture-richardson-tx.geojson'; TMP=OUT.with_suffix('.tmp'); META=OUT.with_suffix('.metadata.json'); METATMP=META.with_suffix('.tmp')
BBOX='-96.731,32.950,-96.727,32.954'
cli_candidates=[
    shutil.which('overturemaps'),
    pathlib.Path(sysconfig.get_path('scripts'))/'overturemaps',
    pathlib.Path(site.getuserbase())/'bin/overturemaps',
]
cli=next((str(candidate) for candidate in cli_candidates if candidate and pathlib.Path(candidate).is_file()),None)
if not cli:
    raise SystemExit('Overture CLI is installed but not discoverable. Install it with: python3 -m pip install --user overturemaps')
OUT.parent.mkdir(parents=True,exist_ok=True)
TMP.unlink(missing_ok=True); METATMP.unlink(missing_ok=True)
try:
    with urllib.request.urlopen('https://stac.overturemaps.org/catalog.json', timeout=30) as response:
        release=json.load(response).get('latest')
    if not release: raise ValueError('STAC catalog did not specify a latest release')
    # The client follows Overture's STAC catalog itself. Supplying -r is not
    # portable across client versions even when the catalog advertises it.
    subprocess.run([cli,'download',f'--bbox={BBOX}','-f','geojson','-t','building','-o',str(TMP),'--connect_timeout','30','--request_timeout','300'],check=True)
    payload=json.loads(TMP.read_text())
    if payload.get('type')!='FeatureCollection' or not isinstance(payload.get('features'),list):
        raise ValueError('Overture did not return a complete GeoJSON FeatureCollection')
    metadata={'provider':'Overture Maps','dataset':'buildings/building','datasetRelease':release,'acquiredAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bbox':[float(v) for v in BBOX.split(',')],'rawRecordCount':len(payload['features']),'schemaVersion':1}
    METATMP.write_text(json.dumps(metadata))
    TMP.replace(OUT); METATMP.replace(META)
    print(json.dumps({'rawRecordCount':metadata['rawRecordCount'],'datasetRelease':release,'rawPath':str(OUT)}))
finally:
    TMP.unlink(missing_ok=True); METATMP.unlink(missing_ok=True)
