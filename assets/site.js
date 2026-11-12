/* ONECODEX — общие скрипты всех страниц */
(function(){
  // === Настройка внешнего приёмника заявок ===
  // LEAD_ENDPOINT — URL серверного обработчика заявок (например, Formspree, Cloudflare Worker).
  // Если пустой или недоступен, будет использоваться фолбэк: Telegram и mailto.
  const LEAD_ENDPOINT = '';

  var YM=112188634;
  function goal(name){ if(typeof ym==='function') ym(YM,'reachGoal',name); }

  var year=document.getElementById('year');
  if(year) year.textContent=new Date().getFullYear();

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

  /* ---------- Отправка заявки из формы ---------- */
  function getUtmParams() {
    const params = {};
    const query = window.location.search.substring(1);
    query.split('&').forEach(function(pair) {
      const [k, v] = pair.split('=');
      if (k) params[decodeURIComponent(k)] = decodeURIComponent(v || '');
    });
    return params;
  }

  function buildLeadText(form) {
    const name = (form.querySelector('#name') || {}).value || '';
    const method = (form.querySelector('input[name="contact_method"]:checked') || {}).value || 'telegram';
    const contact = (form.querySelector('#contact-value') || {}).value || '';
    const message = (form.querySelector('#message') || {}).value || '';
    const page = window.location.href;
    const utm = getUtmParams();

    let lines = [
      'Новая заявка с сайта onecodex.ru',
      '',
      'Имя/компания: ' + name,
      'Способ связи: ' + (method === 'telegram' ? 'Telegram' : method === 'email' ? 'Email' : 'Телефон'),
      'Контакт: ' + contact,
      '',
      'Задача: ' + message,
      '',
      'Страница: ' + page
    ];
    if (utm.utm_source) lines.push('utm_source: ' + utm.utm_source);
    if (utm.utm_medium) lines.push('utm_medium: ' + utm.utm_medium);
    if (utm.utm_campaign) lines.push('utm_campaign: ' + utm.utm_campaign);
    if (utm.utm_term) lines.push('utm_term: ' + utm.utm_term);
    if (utm.utm_content) lines.push('utm_content: ' + utm.utm_content);

    return lines.join('\n');
  }

  function copyTextToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function(resolve, reject) {
      const area = document.createElement('textarea');
      area.value = text;
      area.style.position = 'fixed';
      area.style.left = '-9999px';
      document.body.appendChild(area);
      area.focus();
      try {
        document.execCommand('copy');
        resolve();
      } catch (err) {
        reject(err);
      } finally {
        document.body.removeChild(area);
      }
    });
  }

  function openTelegramFallback(text) {
    const url = 'https://t.me/chvanov_ivan?text=' + encodeURIComponent(text);
    window.open(url, '_blank');
    return true;
  }

  function openMailtoFallback(text) {
    const subject = encodeURIComponent('Новая заявка с сайта OneCodex');
    const body = encodeURIComponent(text);
    const url = 'mailto:hello@onecodex.ru?subject=' + subject + '&body=' + body;
    window.open(url, '_blank');
    return true;
  }

  function showFallbackBlock(form, text) {
    const formBody = form.querySelector('.form-body');
    const formSuccess = form.querySelector('.form-success');
    if (!formBody || !formSuccess) return;

    const fallbackHtml =
      '<div class="fallback-block" style="padding:20px;background:#f5f5f7;border-radius:16px;margin-top:16px">' +
      '  <p style="margin:0 0 12px;font-size:16px">Не удалось отправить через сервер. Воспользуйтесь фолбэком:</p>' +
      '  <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">' +
      '    <a id="mailtoLink" href="#" style="color:var(--link);font-weight:500;text-decoration:underline" target="_blank" rel="noopener">Открыть почту: hello@onecodex.ru ↗</a>' +
      '    <button type="button" id="copyBtn" style="padding:8px 14px;border-radius:999px;border:1px solid var(--accent);background:transparent;color:var(--link);font-size:14px">Скопировать текст</button>' +
      '  </div>' +
      '  <p style="margin-top:12px;font-size:13px;color:var(--muted);line-height:1.4">' +
      '    Или создайте заявку самостоятельно:' +
      '  </p>' +
      '  <p style="margin:6px 0 0;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;color:var(--text);white-space:pre-wrap;background:#fff;padding:10px 12px;border-radius:10px;border:1px solid var(--line2);max-height:160px;overflow:auto">' +
      '    ' + text.replace(/</g, '&lt;').replace(/>/g, '&gt;') +
      '  </p>' +
      '</div>';

    const fallbackDiv = document.createElement('div');
    fallbackDiv.innerHTML = fallbackHtml;
    const fallbackBlock = fallbackDiv.firstElementChild;

    // Подготовим ссылку mailto
    const mailtoLink = fallbackBlock.querySelector('#mailtoLink');
    const subject = 'Новая заявка с сайта OneCodex';
    const bodyText = encodeURIComponent(text);
    mailtoLink.href = 'mailto:hello@onecodex.ru?subject=' + subject + '&body=' + bodyText;

    // Обработчик копирования
    fallbackBlock.querySelector('#copyBtn').addEventListener('click', function () {
      copyTextToClipboard(text).then(function () {
        const btn = this;
        const oldText = btn.textContent;
        btn.textContent = 'Скопировано!';
        setTimeout(function () { btn.textContent = oldText; }, 1500);
      }.bind(this));
    });

    formBody.appendChild(fallbackBlock);
    fallbackBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function processFormSubmission(form, status, submitBtn) {
    const checks = [
      validateName(true, true),
      validateContact(true, true),
      validateMessage(true, true),
      validateConsent(true)
    ];

    if (checks.includes(false)) {
      const bad = form.querySelector('.field.invalid input, .field.invalid textarea') || form.querySelector('#consent');
      if (bad) {
        bad.focus({ preventScroll: true });
        bad.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
      submitBtn.disabled = false;
      submitBtn.textContent = 'Отправить задачу →';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправляем…';

    let openedChannel = false;

    if (LEAD_ENDPOINT && LEAD_ENDPOINT.trim()) {
      const data = {
        name: form.querySelector('#name').value.trim(),
        contact_method: form.querySelector('input[name="contact_method"]:checked').value,
        contact: form.querySelector('#contact-value').value.trim(),
        message: form.querySelector('#message').value.trim(),
        page: location.href
      };
      const utm = getUtmParams();
      if (Object.keys(utm).length) data.utm = utm;

      fetch(LEAD_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) {
        if (r.ok) {
          return r.json();
        }
        throw new Error('not ok');
      }).then(function (j) {
        if (j && j.ok) {
          openedChannel = true;
          form.classList.add('sent');
          form.querySelector('.form-success').scrollIntoView({ block: 'center', behavior: 'smooth' });
          if (typeof ym === 'function') ym(YM, 'reachGoal', 'form_submit');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Отправить задачу →';
          return;
        }
        throw new Error('server error');
      }).catch(function () {
        // Сетевая ошибка или ответ с ошибкой — переходим к фолбэку
        handleFallback(form, status, submitBtn);
      });
    } else {
      handleFallback(form, status, submitBtn);
    }

    function handleFallback(form, status, submitBtn) {
      const text = buildLeadText(form);
      const telegramOpened = openTelegramFallback(text);
      const mailtoOpened = openMailtoFallback(text);

      if (telegramOpened || mailtoOpened) {
        openedChannel = true;
        showFallbackBlock(form, text);
      }

      // Спойлер: если ни один канал не открылся, не показываем «отправлено», не отправляем reachGoal
      if (!openedChannel) {
        status.textContent = 'Не удалось открыть ни один канал связи. Пожалуйста, попробуйте позже или напишите напрямую.';
        status.classList.add('show', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить задачу →';
        return;
      }

      form.classList.add('sent');
      form.querySelector('.form-success').scrollIntoView({ block: 'center', behavior: 'smooth' });
      if (typeof ym === 'function') ym(YM, 'reachGoal', 'form_submit');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Отправить задачу →';
    }
  }

  document.querySelectorAll('.case-live').forEach(function(a){a.addEventListener('click',function(){goal('case_live_click');});});
})();
