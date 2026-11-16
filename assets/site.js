/* ONECODEX — общие скрипты всех страниц */
(function(){
  var YM=112188634;
  function goal(name){ if(typeof ym==='function') ym(YM,'reachGoal',name); }

  var year=document.getElementById('year');
  if(year) year.textContent=new Date().getFullYear();

  /* ---------- UTM-атрибуция ---------- */
  (function(){
    var KEY='onecodex_utm';
    function parseUrl(){
      var params=new URLSearchParams(location.search);
      var utm={
        source:params.get('utm_source')||'',
        medium:params.get('utm_medium')||'',
        campaign:params.get('utm_campaign')||'',
        content:params.get('utm_content')||''
      };
      if(utm.source||utm.medium||utm.campaign||utm.content){
        return utm;
      }
      // Если utm нет, определяем источник по рефереру
      var ref=location.referrer||document.referrer||'';
      if(ref){
        try{
          var u=new URL(ref);
          var host=u.hostname.toLowerCase();
          if(host.includes('t.me')||host.includes('telegram.me')) return {source:'telegram',medium:'referral',campaign:'direct',content:''};
          if(host.includes('spros.work')) return {source:'spros',medium:'referral',campaign:'direct',content:''};
          // Для прочих рефереров — домен как источник
          if(host){
            var domain=host.replace(/^www\./,'');
            return {source:domain,medium:'referral',campaign:'direct',content:''};
          }
        }catch(_){}
      }
      // Если ничего не определили — direct
      return {source:'direct',medium:'none',campaign:'direct',content:''};
    }
    try{
      var stored=sessionStorage.getItem(KEY);
      if(stored){
        var saved=JSON.parse(stored);
        if(saved.time&&Date.now()-saved.time<3600000){ // 1 час — сохраняем метку на сессию
          window.onecodex_utm=saved.data;
        }else{
          window.onecodex_utm=parseUrl();
          sessionStorage.setItem(KEY,JSON.stringify({time:Date.now(),data:window.onecodex_utm}));
        }
      }else{
        window.onecodex_utm=parseUrl();
        sessionStorage.setItem(KEY,JSON.stringify({time:Date.now(),data:window.onecodex_utm}));
      }
    }catch(_){
      window.onecodex_utm={source:'direct',medium:'none',campaign:'direct',content:''};
    }
  })();

  /* Мобильное меню */
  var burger=document.querySelector('.burger'), nav=document.querySelector('.navlinks');
  if(burger&&nav){
    burger.addEventListener('click',function(){
      var open=nav.classList.toggle('open');
      burger.setAttribute('aria-expanded',open);
      burger.textContent=open?'✕':'☰';
    });
    nav.addEventListener('click',function(e){
      if(e.target.closest('a')){nav.classList.remove('open');burger.setAttribute('aria-expanded','false');burger.textContent='☰';}
    });
  }

  /* Кнопка «Наверх» */
  var top=document.createElement('a');
  top.href='#';top.className='to-top';top.setAttribute('aria-label','Наверх');
  top.innerHTML='<span aria-hidden="true">↑</span><span>Наверх</span>';
  top.addEventListener('click',function(e){e.preventDefault();scrollTo({top:0,behavior:'smooth'});});
  document.body.appendChild(top);
  addEventListener('scroll',function(){top.classList.toggle('show',scrollY>700);},{passive:true});

  /* Cookie-баннер */
  var KEY='onecodex_cookie_ok', accepted=false;
  try{accepted=localStorage.getItem(KEY)==='1';}catch(_){}
  if(!accepted){
    var c=document.createElement('div');
    c.className='cookie';c.setAttribute('role','dialog');c.setAttribute('aria-label','Использование cookie');
    c.innerHTML='<p>Мы используем cookie и Яндекс.Метрику, чтобы сайт работал корректно и становился удобнее. Подробнее — в <a href="privacy.html">политике конфиденциальности</a>.</p><button type="button" class="btn">Принять</button>';
    document.body.appendChild(c);
    var setH=function(){document.documentElement.style.setProperty('--cookie-h',(c.hidden?0:c.offsetHeight+16)+'px');};
    setH();addEventListener('resize',setH);
    c.querySelector('button').addEventListener('click',function(){
      try{localStorage.setItem(KEY,'1');}catch(_){}
      c.hidden=true;setH();
    });
  }

  /* Подсказки у коротких пунктов на первом экране (тап на мобильных) */
  document.querySelectorAll('.chip').forEach(function(ch){
    ch.addEventListener('click',function(){
      var was=ch.classList.contains('open');
      document.querySelectorAll('.chip.open').forEach(function(x){x.classList.remove('open');});
      if(!was) ch.classList.add('open');
    });
  });
  document.addEventListener('click',function(e){
    if(!e.target.closest('.chip')) document.querySelectorAll('.chip.open').forEach(function(x){x.classList.remove('open');});
  });

  /* Переключатель версий первого экрана: ?hero=tech открывает техническую сразу (для A/B) */
  var hero=document.querySelector('.hero');
  var sw=document.querySelectorAll('.hero-switch button');
  function setHero(v){
    if(!hero) return;
    hero.classList.toggle('is-tech',v==='tech');
    sw.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.v===v);});
  }
  sw.forEach(function(b){b.addEventListener('click',function(){setHero(b.dataset.v);goal('hero_'+b.dataset.v);});});
  if(/[?&]hero=tech\b/.test(location.search)) setHero('tech');

  /* Карусель преимуществ */
  document.querySelectorAll('.carousel').forEach(function(car){
    var track=car.querySelector('.car-track'), prev=car.querySelector('[data-dir="-1"]'), next=car.querySelector('[data-dir="1"]');
    var dots=car.querySelector('.car-dots'), items=track.children;
    if(dots) for(var i=0;i<items.length;i++) dots.appendChild(document.createElement('i'));
    function step(){return items[0].getBoundingClientRect().width+16;}
    function upd(){
      var max=track.scrollWidth-track.clientWidth-2;
      if(prev) prev.disabled=track.scrollLeft<=2;
      if(next) next.disabled=track.scrollLeft>=max;
      if(dots){var idx=Math.round(track.scrollLeft/step());
        [].forEach.call(dots.children,function(d,j){d.classList.toggle('on',j===Math.min(idx,items.length-1));});}
    }
    [prev,next].forEach(function(b){ if(b) b.addEventListener('click',function(){track.scrollBy({left:step()*+b.dataset.dir,behavior:'smooth'});}); });
    track.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd();
  });

  /* Вкладки кейсов */
  var tabs=document.querySelectorAll('.tab[data-filter]');
  tabs.forEach(function(t){
    t.addEventListener('click',function(){
      var f=t.dataset.filter;
      tabs.forEach(function(x){x.setAttribute('aria-selected',x===t);});
      document.querySelectorAll('.case[data-cat]').forEach(function(c){
        c.hidden=!(f==='all'||c.dataset.cat.split(' ').indexOf(f)>=0);
      });
    });
  });

  /* «Хочу так же» / «Хочу ещё лучше»: подставляем текст в форму */
  document.querySelectorAll('[data-want]').forEach(function(b){
    b.addEventListener('click',function(){
      goal('want_click');
      var msg=b.dataset.want;
      try{sessionStorage.setItem('onecodex_want',msg);}catch(_){}
      var ta=document.getElementById('message');
      if(ta&&!ta.value.trim()) ta.value=msg;
    });
  });
  var ta=document.getElementById('message');
  if(ta){ try{var saved=sessionStorage.getItem('onecodex_want'); if(saved&&!ta.value.trim()&&location.hash==='#contact'){ta.value=saved;} }catch(_){} }

  /* Цели Метрики */
  document.querySelectorAll('a[href^="tel:"]').forEach(function(a){a.addEventListener('click',function(){goal('phone_click');});});
  document.querySelectorAll('a[href*="t.me/"]').forEach(function(a){a.addEventListener('click',function(){goal('telegram_click');});});
  document.querySelectorAll('a[href^="service-"]').forEach(function(a){a.addEventListener('click',function(){goal('service_click');});});
  document.querySelectorAll('a[href^="case-"]').forEach(function(a){a.addEventListener('click',function(){goal('case_click');});});
  document.querySelectorAll('.case-live').forEach(function(a){a.addEventListener('click',function(){goal('case_live_click');});});

  /* ---------- Атрибуция ссылок на Telegram ---------- */
  (function(){
    if(!window.onecodex_utm) return;
    var utm=window.onecodex_utm;
    // Получаем UTM-параметры для ссылок, добавляя utm_source с указанием страницы
    var getUtmForLink=function(prefix){
      var utmParams=new URLSearchParams();
      utmParams.set('utm_source',prefix||'site_index');
      utmParams.set('utm_medium',utm.medium||'link');
      if(utm.campaign) utmParams.set('utm_campaign',utm.campaign);
      if(utm.content) utmParams.set('utm_content',utm.content);
      return utmParams.toString();
    };
    // Добавляем utm к всем ссылкам t.me на странице (если ещё нет utm_source)
    var pageId='index';
    if(document.body.classList.contains('service-page')) pageId='service';
    document.querySelectorAll('a[href^="https://t.me/"]').forEach(function(a){
      var href=a.getAttribute('href');
      if(href.indexOf('utm_source=')<0){
        var sep=href.indexOf('?')>=0?'&':'?';
        var utmStr=getUtmForLink('site_'+pageId);
        a.href=href+sep+utmStr;
      }
    });
  })();

  /* ---------- Атрибуция формы заявки ---------- */
  (function(){
    if(!window.onecodex_utm) return;
    var utm=window.onecodex_utm;
    var form=document.getElementById('contactForm');
    if(!form) return;

    // Создаём скрытые поля для UTM
    var createHiddenField=function(name,value){
      var input=document.createElement('input');
      input.type='hidden';
      input.name=name;
      input.value=value||'';
      return input;
    };

    // Обновляем поля при каждом открытии формы (если она ресетится)
    var updateFormFields=function(){
      // Удаляем старые поля, если есть
      ['source','utm_source','utm_medium','utm_campaign'].forEach(function(name){
        var el=form.querySelector('input[name="'+name+'"]');
        if(el) el.remove();
      });

      // Добавляем новые
      var sourceEl=createHiddenField('source',utm.source||'direct');
      var utmSourceEl=createHiddenField('utm_source',utm.source||'');
      var utmMediumEl=createHiddenField('utm_medium',utm.medium||'');
      var utmCampaignEl=createHiddenField('utm_campaign',utm.campaign||'');
      form.appendChild(sourceEl);
      form.appendChild(utmSourceEl);
      form.appendChild(utmMediumEl);
      form.appendChild(utmCampaignEl);

      // Добавляем метку в начало поля message (так как send.php не принимает utm-поля)
      var msgInput=document.getElementById('message');
      if(msgInput){
        var existing=msgInput.value;
        var utmInfo='';
        if(utm.source) utmInfo+='Источник: '+utm.source+'\n';
        if(utm.medium) utmInfo+='Канал: '+utm.medium+'\n';
        if(utm.campaign) utmInfo+='Кампания: '+utm.campaign+'\n';
        if(utmInfo){
          msgInput.value=utmInfo+'\n---\n'+existing;
        }
      }
    };

    // Вызываем сразу
    updateFormFields();

    // Обновляем при ресете формы (кнопка «Отправить ещё одну задачу»)
    var againBtn=document.getElementById('againBtn');
    if(againBtn){
      againBtn.addEventListener('click',function(){
        setTimeout(updateFormFields,0);
      });
    }
  })();
})();
