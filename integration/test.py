"""Native HTTP integration checks; fixture databases never use the local demo data."""
import sys,os,json,re,time,secrets,socket,subprocess,tempfile,shutil,sqlite3,hashlib,gc
from pathlib import Path
from urllib.request import Request,build_opener,HTTPCookieProcessor
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode
from http.cookiejar import CookieJar
ROOT=Path(__file__).resolve().parent.parent
DJANGO=(ROOT/'manage.py').exists()

if len(sys.argv)>1 and sys.argv[1]=='--serve':
    folder=Path(sys.argv[2]);port=int(sys.argv[3]);sys.path.insert(0,str(ROOT));sys.path.insert(0,str(folder))
    if DJANGO:
        import django
        django.setup()
        from django.core.management import call_command
        call_command('migrate',verbosity=0,interactive=False)
        from django.contrib.auth import get_user_model
        get_user_model().objects.create_superuser(email='admin@example.org',password='Integration123!',first_name='AdminPrivate',last_name='Fixture')
        from library.models import Book,Member
        Book.objects.create(title='SharedCatalogSecret',author='UnrelatedAuthor',category='fiction',quantity=2,borrowing_fee=1)
        Member.objects.create(name='SharedMemberSecret',email='unrelated@example.org')
        call_command('runserver',f'127.0.0.1:{port}',use_reloader=False,verbosity=0)
    else:
        from app.main import app
        from app.db import create_tables
        import uvicorn
        create_tables()
        uvicorn.run(app,host='127.0.0.1',port=port,log_level='warning')
    raise SystemExit

class Client:
    def __init__(self):
        self.opener=build_opener(HTTPCookieProcessor(CookieJar()));self.token=None
    def request(self,path,body=None,method='GET',headers=None):
        headers=dict(headers or {})
        if self.token:headers['Authorization']='Bearer '+self.token
        if body is not None and not isinstance(body,(str,bytes)):
            body=json.dumps(body);headers.setdefault('Content-Type','application/json')
        if isinstance(body,str):body=body.encode()
        req=Request(base+path,data=body,method=method,headers=headers)
        try:
            with self.opener.open(req,timeout=15) as res:status,raw,url=res.status,res.read().decode(),res.url
        except HTTPError as e:status,raw,url=e.code,e.read().decode(),e.url
        try:data=json.loads(raw)
        except ValueError:data=raw
        return status,data,url
    def form(self,path,values):
        status,html,_=self.request(path)
        token=re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',html)
        if not token:raise RuntimeError('Original form CSRF missing')
        return self.request(path,urlencode({'csrfmiddlewaretoken':token[1],**values}),'POST',{'Content-Type':'application/x-www-form-urlencoded','Referer':base+path})
    def signup(self,name,email):
        if DJANGO:
            return self.form('/register/',{'first_name':name,'last_name':'Fixture','email':email,'password':'Integration123!','repeat_password':'Integration123!'})
        return self.request('/resister',{'userName':name,'name':name,'email':email,'password':'Integration123!'},'POST')
    def login(self,name,email):
        if DJANGO:return self.form('/login/',{'email':email,'password':'Integration123!'})
        reply=self.request('/login',urlencode({'username':name,'password':'Integration123!'}),'POST',{'Content-Type':'application/x-www-form-urlencoded'})
        self.token=reply[1].get('access token');return reply
    def csrf(self):return self.request('/gdpr/csrf/')[1]['token']
    def api(self,operation,value=None,method='POST',token=True):
        headers={'Content-Type':'application/json'}
        if DJANGO and token is not False:headers['X-CSRFToken']=self.csrf() if token is True else token
        return self.request('/gdpr/'+operation+('/' if DJANGO else ''),{} if value is None else value,method,headers)

def port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def check(name,passed):
    global checks
    if not passed:raise RuntimeError(name)
    checks+=1;print('PASS '+name,flush=True)
def stop(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
def hashes():
    files=[ROOT/'integration/privacy_lib/gdpr_router.py',*sorted((ROOT/'integration/privacy_lib/gdpr').glob('*.rego'))]
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

checks=0;app=None;opa=None;original=hashes();folder=Path(tempfile.mkdtemp(prefix='privacy-python-check-'));log=None;exit_code=0
try:
    app_port,opa_port=port(),port();base=f'http://127.0.0.1:{app_port}'
    env=os.environ.copy();secret=secrets.token_hex(32);env.update(SECRET_KEY=secret,ALGORITHM='HS256',OPA_QUERY_URL=f'http://127.0.0.1:{opa_port}/v1/query',GDPR_ADMIN_USER_IDS='AlphaPrivate',PYTHONDONTWRITEBYTECODE='1')
    database=folder/'fixture.sqlite3'
    if DJANGO:
        settings_file=folder/'privacy_fixture_settings.py'
        settings_file.write_text("from core.settings import *\nDATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':"+repr(str(database))+"}}\nDEBUG=False\nALLOWED_HOSTS=['127.0.0.1','localhost']\nEMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'\n",encoding='utf-8')
        env.update(DJANGO_SETTINGS_MODULE='privacy_fixture_settings',POSTGRES_DB='unused',POSTGRES_USER='unused',POSTGRES_PASSWORD='unused',POSTGRES_HOST='127.0.0.1',POSTGRES_PORT='5432')
    else:env['SQLALCHEMY_DATABASE_URL']='sqlite:///'+str(database)
    env['PYTHONPATH']=os.pathsep.join([str(ROOT),str(folder)])
    log=(folder/'server.log').open('w',encoding='utf-8')
    opa=subprocess.Popen([os.environ.get('OPA_BINARY','opa'),'run','--server','--addr',f'127.0.0.1:{opa_port}',str(ROOT/'integration/privacy_lib/gdpr')],cwd=ROOT,env=env,stdout=log,stderr=log)
    app=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--serve',str(folder),str(app_port)],cwd=ROOT,env=env,stdout=log,stderr=log)
    anon=Client();ready=False
    for _ in range(200):
        if app.poll() is not None:raise RuntimeError('Fixture app stopped during startup')
        try:
            if anon.request('/login/' if DJANGO else '/docs')[0]==200:
                with socket.create_connection(('127.0.0.1',opa_port),timeout=.2):ready=True
                break
        except (OSError,URLError):pass
        time.sleep(.1)
    if not ready:raise RuntimeError('Fixture startup timed out')
    check('Original login/docs interface renders',anon.request('/login/' if DJANGO else '/docs')[0]==200)
    check('Anonymous private API denied',anon.request('/gdpr/csrf/' if DJANGO else '/gdpr/profile')[0]==401)
    check('Anonymous mutation denied',anon.api('consent',token=False)[0] in (401,403))
    alice,bob=Client(),Client()
    check('Original Alice registration',alice.signup('AlphaPrivate','alpha@example.org')[0]==200)
    check('Original Alice login',alice.login('AlphaPrivate','alpha@example.org')[0]==200)
    if DJANGO:
        db=sqlite3.connect(database);alice_id=db.execute("SELECT id FROM users_librarian WHERE email='alpha@example.org'").fetchone()[0];db.close()
        check('Native authenticated dashboard links privacy', 'Privacy checks' in alice.request('/')[1])
        check('Native privacy page renders actual identity','alpha@example.org' in alice.request('/gdpr/')[1])
        check('Missing CSRF denied',alice.api('consent',token=False)[0]==403)
        check('Invalid CSRF denied',alice.api('consent',token='invalid')[0]==403)
    else:
        alice_id='AlphaPrivate'
        check('Original JWT resolves persisted profile',alice.request('/gdpr/profile')[1]['userName']=='AlphaPrivate')
        check('Public privacy shell contains no embedded profile', 'alpha@example.org' not in anon.request('/gdpr')[1])
        from jose import jwt
        bad=Client();bad.token='not.a.valid.token'
        check('Malformed bearer denied',bad.request('/gdpr/profile')[0]==401)
        bad.token=jwt.encode({'sub':'AlphaPrivate','exp':time.time()+60},'wrong-secret',algorithm='HS256')
        check('Wrong JWT signature denied',bad.request('/gdpr/profile')[0]==401)
        bad.token=jwt.encode({'sub':'AlphaPrivate','exp':time.time()-60},secret,algorithm='HS256')
        check('Expired JWT denied',bad.request('/gdpr/profile')[0]==401)
        bad.token=jwt.encode({'sub':'AlphaPrivate'},secret,algorithm='HS256')
        check('JWT without expiry denied',bad.request('/gdpr/profile')[0]==401)
        bad.token=jwt.encode({'sub':'missing-user','exp':time.time()+60},secret,algorithm='HS256')
        check('JWT for nonexistent subject denied',bad.request('/gdpr/profile')[0]==401)
    check('Missing consent rejects processing',alice.api('consent')[1] is False)
    granted={'value':'yes','withdrawn':False}
    check('Consent persistence response',alice.api('consent',granted,'PATCH')[1]==granted)
    db=sqlite3.connect(database)
    stored=db.execute('SELECT user_id,value,withdrawn FROM privacy_consent' if DJANGO else 'SELECT user_name,value,withdrawn FROM gdpr_consents').fetchone();db.close()
    check('Stored consent belongs to authenticated subject',str(stored[0])==str(alice_id) and stored[1:] == ('yes',0))
    for operation in ['consent','lawful']:check(operation+' accepts stored consent',alice.api(operation)[1] is True)
    check('Information uses saved consent',alice.api('information')[1]['consent_valid'] is True)
    access=alice.api('access')[1];metadata=json.loads(access['download']['content']);fields=sorted(x['field'] for x in metadata['data_collected_from_user'])
    expected=['date_joined','email','first_name','last_name'] if DJANGO else ['created_at','email','name','userName']
    check('Access maps exact stored profile fields',metadata['user_id']==str(alice_id) and fields==expected)
    mutable='first_name' if DJANGO else 'name'
    rect=alice.api('rectification',{'updates':{mutable:'Updated'}})[1]
    check('Rectification returns current-subject plan',rect['request']['validated'] and any(x['user_id']==str(alice_id) and x['field']==mutable for x in rect['db_update_plan']))
    check('Retention exception rejects email erasure',alice.api('erasure',{'fields':['email']})[1]['decision']=='reject')
    check('Restriction returns acceptance plan',alice.api('restriction')[1]['decision']=='accept')
    export=alice.api('portability')[1];text=json.dumps(export)
    check('Portability exports actual profile in two formats',export['decision']=='accept' and len(export['actions']['downloads'])==2 and 'alpha@example.org' in text and 'AlphaPrivate' in text)
    check('Passwords and tokens excluded','Integration123' not in text and 'password' not in text and 'access token' not in text)
    if DJANGO:check('Shared catalogue/member data excluded','SharedCatalogSecret' not in text and 'SharedMemberSecret' not in text and 'UnrelatedAuthor' not in text)
    check('Objection returns stop plan',alice.api('objection',{'reason':'marketing'})[1]['decision']=='accept')
    check('Complaint returns forwarding plan',alice.api('complaint',{'authority_id':'cy-0000','description':'Synthetic test only'})[1]['decision']=='accept')
    if DJANGO:
        check('Ordinary librarian breach denied',alice.api('breach',{'incident_id':'test'})[0]==403)
        admin=Client();check('Original administrator login',admin.login('unused','admin@example.org')[0]==200)
        check('Native administrator breach assessment',admin.api('breach',{'incident_id':'test'})[1]['decision']=='notify_users')
        admin.api('consent',granted,'PATCH');admin_export=json.dumps(admin.api('portability')[1])
        check('Administrator export excludes other profiles/catalogue','alpha@example.org' not in admin_export and 'SharedCatalogSecret' not in admin_export)
    else:check('Configured administrator breach assessment',alice.api('breach',{'incident_id':'test'})[1]['decision']=='notify_users')
    check('Original Bob registration',bob.signup('BetaPrivate','beta@example.org')[0]==200)
    check('Original Bob login',bob.login('BetaPrivate','beta@example.org')[0]==200)
    check('Second user has independent consent',bob.api('consent')[1] is False)
    check('Non-admin breach denied',bob.api('breach',{'incident_id':'test'})[0]==403)
    bob.api('consent',granted,'PATCH');bob_text=json.dumps(bob.api('portability')[1])
    check('Bob export excludes Alice','beta@example.org' in bob_text and 'alpha@example.org' not in bob_text)
    check('Alice export excludes Bob','beta@example.org' not in json.dumps(alice.api('portability')[1]))
    check('Client cannot select another subject',bob.api('access',{'user_id':alice_id})[0]==400)
    check('Client cannot override trusted checks',alice.api('restriction',{'checks':{'data_correct':True}})[0]==400)
    if DJANGO:check('Cross-session CSRF denied',bob.api('consent',token=alice.csrf())[0]==403)
    check('Strict boolean validation',alice.api('consent',{'value':'yes','withdrawn':'false'},'PATCH')[0]==400)
    check('Unknown policy rejected',alice.api('unknown')[0]==400)
    check('Malformed JSON rejected',alice.api('consent','{')[0]==400)
    check('Array JSON rejected',alice.api('consent','[]')[0]==400)
    check('Nonfinite JSON rejected',alice.api('breach','{"incident_id":"x","hours_since_detected":NaN}')[0]==400)
    check('Oversized JSON rejected',alice.api('consent','x'*16385)[0]==413)
    check('Unsupported method rejected',alice.request('/gdpr/consent'+('/' if DJANGO else ''))[0]==405)
    check('Invalid content type rejected',alice.request('/gdpr/consent'+('/' if DJANGO else ''),'{}','PATCH',{'Content-Type':'text/plain',**({'X-CSRFToken':alice.csrf()} if DJANGO else {})})[0]==415)
    check('Consent withdrawal saved',alice.api('consent',{'value':'yes','withdrawn':True},'PATCH')[0]==200)
    for operation in ['consent','lawful']:check(operation+' rejects withdrawn consent',alice.api(operation)[1] is False)
    check('Portability rejects withdrawal',alice.api('portability')[1]['decision']=='reject')
    check('Access remains available after withdrawal',alice.api('access')[1]['request']['validated'] is True)
    check('Eligible erasure returns plan',alice.api('erasure',{'fields':[mutable],'reason':'withdrawn_consent'})[1]['decision']=='accept')
    db=sqlite3.connect(database);saved=db.execute("SELECT first_name FROM users_librarian WHERE email='alpha@example.org'" if DJANGO else 'SELECT name FROM users WHERE "userName"=\'AlphaPrivate\'').fetchone()[0];db.close()
    check('Plans did not change profile',saved=='AlphaPrivate')
    if DJANGO:
        alice.request('/logout/');check('Original logout invalidates privacy access',alice.request('/gdpr/csrf/')[0]==401)
        check('Original login still works',alice.login('AlphaPrivate','alpha@example.org')[0]==200)
    stop(opa);check('OPA outage returns 502',alice.api('consent')[0]==502)
    check('Bundled router and Rego hashes unchanged',hashes()==original)
    # Report success only after temporary processes and files are cleaned.
except Exception as exc:
    print('FAIL '+str(exc),file=sys.stderr)
    if log:log.flush();print((folder/'server.log').read_text(encoding='utf-8',errors='replace')[-5000:],file=sys.stderr)
    exit_code=1
finally:
    stop(app);stop(opa)
    if log:log.close()
    if isinstance(globals().get('db'), sqlite3.Connection):
        db.close()
    db=None
    gc.collect()
    if folder.parent.resolve()!=Path(tempfile.gettempdir()).resolve() or not folder.name.startswith('privacy-python-check-'):
        raise RuntimeError('Unsafe fixture cleanup path')
    for attempt in range(15):
        try:
            shutil.rmtree(folder)
            break
        except PermissionError:
            if attempt==14:raise
            gc.collect();time.sleep(.2)
if exit_code==0:print(f'Integration result: {checks}/{checks} passed',flush=True)
sys.exit(exit_code)
