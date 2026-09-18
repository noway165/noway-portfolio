/* ==========================================================================
   Tăng Thoại Lâm — Portfolio
   Một file cho cả web. Mỗi khối tự kiểm tra phần tử của nó trước khi chạy,
   nên trang nào không có phần tử đó thì khối đó tự bỏ qua.
   ========================================================================== */
(() => {
    'use strict';

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ---------------------------------------------- 1. VIỀN MENU KHI CUỘN */
    function initNavScroll() {
        const nav = document.getElementById('siteNav');
        if (!nav) return;
        const update = () => nav.classList.toggle('is-scrolled', window.scrollY > 10);
        window.addEventListener('scroll', update, { passive: true });
        update();
    }

    /* ---------------------------------------------- 2. HIỆN DẦN KHI CUỘN */
    function initReveal() {
        const items = document.querySelectorAll('.reveal');
        if (!items.length) return;

        if (reduceMotion || !('IntersectionObserver' in window)) {
            items.forEach((el) => el.classList.add('is-in'));
            return;
        }

        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                setTimeout(() => el.classList.add('is-in'), Number(el.dataset.delay) || 0);
                io.unobserve(el);
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

        items.forEach((el) => io.observe(el));
    }

    /* ---------------------------------------------- 3. CHỮ TỰ GÕ (TRANG CHỦ) */
    function initTypewriter() {
        const el = document.getElementById('typewriter');
        if (!el || reduceMotion) return;

        const words = (el.dataset.words || '').split('|').filter(Boolean);
        if (words.length < 2) return;

        // Server đã in sẵn từ đầu tiên — bắt đầu bằng việc xóa nó đi
        let w = 0;
        let c = words[0].length;
        let deleting = true;

        const tick = () => {
            c += deleting ? -1 : 1;
            el.textContent = words[w].slice(0, c);

            let wait = deleting ? 45 : 95;
            if (!deleting && c === words[w].length) {
                wait = 1900;
                deleting = true;
            } else if (deleting && c === 0) {
                deleting = false;
                w = (w + 1) % words.length;
                wait = 420;
            }
            setTimeout(tick, wait);
        };
        setTimeout(tick, 2200);
    }

    /* ---------------------------------------------- 4. ĐẾM SỐ THỐNG KÊ */
    function initCounters() {
        const nums = document.querySelectorAll('[data-count]');
        if (!nums.length || reduceMotion || !('IntersectionObserver' in window)) return;

        const run = (el) => {
            const target = Number(el.dataset.count);
            const start = performance.now();
            const step = (now) => {
                const p = Math.min((now - start) / 1300, 1);
                el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
                if (p < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
        };

        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                run(entry.target);
                io.unobserve(entry.target);
            });
        }, { threshold: 0.5 });

        nums.forEach((el) => {
            el.textContent = '0';
            io.observe(el);
        });
    }

    /* ---------------------------------------------- 5. XEM ẢNH PHÓNG TO (ALBUM) */
    function initLightbox() {
        const modalEl = document.getElementById('lightbox');
        if (!modalEl || !window.bootstrap) return;

        const carouselEl = modalEl.querySelector('.carousel');
        const slides = [...carouselEl.querySelectorAll('.carousel-item')];
        const counter = document.getElementById('lbCount');

        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        // keyboard: false — phím mũi tên do khối bên dưới xử lý, tránh trượt 2 lần
        const carousel = bootstrap.Carousel.getOrCreateInstance(carouselEl, {
            interval: false, ride: false, keyboard: false, touch: true, wrap: true,
        });

        const setCount = (i) => { if (counter) counter.textContent = `${i + 1} / ${slides.length}`; };

        document.querySelectorAll('[data-photo-index]').forEach((thumb) => {
            thumb.addEventListener('click', () => {
                const i = Number(thumb.dataset.photoIndex);
                // Đặt thẳng ảnh được chọn, không chạy hiệu ứng trượt khi modal đang đóng
                slides.forEach((s, n) => s.classList.toggle('active', n === i));
                setCount(i);
                modal.show();
            });
        });

        carouselEl.addEventListener('slid.bs.carousel', (e) => setCount(e.to));

        document.addEventListener('keydown', (e) => {
            if (!modalEl.classList.contains('show')) return;
            if (e.key === 'ArrowLeft') carousel.prev();
            if (e.key === 'ArrowRight') carousel.next();
        });
    }

    /* ---------------------------------------------- 6. CHÉP ID (LIÊN HỆ) */
    async function copyText(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            }
        } catch (_) { /* thử cách cũ bên dưới */ }

        const ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        let ok = false;
        try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
        ta.remove();
        return ok;
    }

    function initCopy() {
        const buttons = document.querySelectorAll('[data-copy]');
        if (!buttons.length) return;

        const toastEl = document.getElementById('copyToast');
        const toastText = document.getElementById('copyToastText');
        const toast = toastEl && window.bootstrap
            ? bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 2200 })
            : null;

        buttons.forEach((btn) => {
            btn.addEventListener('click', async () => {
                const text = btn.dataset.copy;
                const ok = await copyText(text);
                if (!toast) return;
                toastText.textContent = ok ? `Đã chép “${text}”` : `Không chép được — hãy chép tay: ${text}`;
                toast.show();
            });
        });
    }

    /* ---------------------------------------------- 7. SÁNG / TỐI */
    function initTheme() {
        const btn = document.getElementById('themeToggle');
        const root = document.documentElement;
        const meta = document.querySelector('meta[name="theme-color"]');
        const system = window.matchMedia('(prefers-color-scheme: light)');

        const stored = () => { try { return localStorage.getItem('theme'); } catch (_) { return null; } };
        const current = () => root.getAttribute('data-bs-theme');

        const apply = (theme) => {
            root.setAttribute('data-bs-theme', theme);
            if (meta) meta.setAttribute('content', getComputedStyle(root).getPropertyValue('--bg').trim());
            if (btn) btn.setAttribute('aria-label', theme === 'dark' ? 'Chuyển sang giao diện sáng' : 'Chuyển sang giao diện tối');
        };
        apply(current());

        // Chưa tự chọn lần nào thì đi theo cài đặt của máy
        system.addEventListener('change', (e) => { if (!stored()) apply(e.matches ? 'light' : 'dark'); });

        if (!btn) return;
        btn.addEventListener('click', () => {
            const next = current() === 'dark' ? 'light' : 'dark';
            try { localStorage.setItem('theme', next); } catch (_) { /* chế độ ẩn danh */ }

            if (reduceMotion) return apply(next);

            // Không có View Transition: đổi màu êm bằng transition thường
            if (!document.startViewTransition) {
                root.classList.add('theme-fade');
                apply(next);
                setTimeout(() => root.classList.remove('theme-fade'), 500);
                return;
            }

            // Có View Transition: giao diện mới loang ra thành vòng tròn từ nút bấm
            const r = btn.getBoundingClientRect();
            const x = r.left + r.width / 2;
            const y = r.top + r.height / 2;
            const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));

            root.classList.add('theme-switching');
            const vt = document.startViewTransition(() => apply(next));
            vt.ready.then(() => {
                root.animate(
                    { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
                    { duration: 650, easing: 'cubic-bezier(0.22, 0.61, 0.36, 1)', pseudoElement: '::view-transition-new(root)' },
                );
            }).catch(() => {});
            vt.finished.finally(() => root.classList.remove('theme-switching'));
        });
    }

    /* ---------------------------------------------- 8. THANH TIẾN ĐỘ + NÚT LÊN ĐẦU */
    function initScrollUi() {
        const bar = document.getElementById('scrollProgress');
        const toTop = document.getElementById('toTop');
        let queued = false;

        const update = () => {
            queued = false;
            const max = document.documentElement.scrollHeight - innerHeight;
            const p = max > 0 ? Math.min(scrollY / max, 1) : 0;
            if (bar) bar.style.setProperty('--p', p.toFixed(4));
            if (toTop) toTop.classList.toggle('is-on', scrollY > innerHeight * 0.8);
        };
        const onScroll = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };

        addEventListener('scroll', onScroll, { passive: true });
        addEventListener('resize', onScroll, { passive: true });
        update();

        if (toTop) toTop.addEventListener('click', () => scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }));
    }

    /* ---------------------------------------------- 9. HIỆU ỨNG THEO CHUỘT */
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    // Quầng sáng trong thẻ chạy theo con trỏ
    function initSpotlight() {
        if (!finePointer) return;
        document.querySelectorAll('.tile, .lux-card, .project, .game-card').forEach((el) => {
            el.addEventListener('pointermove', (e) => {
                const r = el.getBoundingClientRect();
                el.style.setProperty('--mx', `${e.clientX - r.left}px`);
                el.style.setProperty('--my', `${e.clientY - r.top}px`);
            });
        });
    }

    // Quầng sáng ở hero nhích nhẹ ngược chiều chuột
    function initHeroGlow() {
        const hero = document.querySelector('.hero');
        if (!hero || !finePointer || reduceMotion) return;
        hero.addEventListener('pointermove', (e) => {
            const r = hero.getBoundingClientRect();
            const dx = (e.clientX - r.left) / r.width - 0.5;
            const dy = (e.clientY - r.top) / r.height - 0.5;
            hero.style.setProperty('--hx', `${(dx * -60).toFixed(1)}px`);
            hero.style.setProperty('--hy', `${(dy * -60).toFixed(1)}px`);
        });
    }

    // Vòng tròn đi theo con trỏ, phình ra khi rê lên thứ bấm được
    function initCursor() {
        if (!finePointer || reduceMotion) return;

        const ring = document.createElement('div');
        ring.className = 'cursor-ring';
        ring.setAttribute('aria-hidden', 'true');
        document.body.appendChild(ring);

        let tx = -100, ty = -100, x = tx, y = ty;
        const loop = () => {
            x += (tx - x) * 0.2;
            y += (ty - y) * 0.2;
            ring.style.transform = `translate3d(${x}px, ${y}px, 0)`;
            requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);

        const clickable = 'a, button, [role="button"], label, .shot';
        document.addEventListener('pointermove', (e) => {
            tx = e.clientX;
            ty = e.clientY;
            ring.classList.add('is-on');
            ring.classList.toggle('is-hover', !!e.target.closest(clickable));
        }, { passive: true });
        document.addEventListener('pointerdown', () => ring.classList.add('is-down'));
        document.addEventListener('pointerup', () => ring.classList.remove('is-down'));
        document.documentElement.addEventListener('pointerleave', () => ring.classList.remove('is-on'));
        // Vào iframe Spotify thì trang không nhận được chuột nữa — ẩn vòng đi
        document.querySelectorAll('iframe').forEach((f) => f.addEventListener('pointerenter', () => ring.classList.remove('is-on')));
    }

    /* ---------------------------------------------- 10. TƯƠNG TÁC: TIM, CHIA SẺ, FORM */
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';

    function toastSay(text) {
        const el = document.getElementById('copyToast');
        if (!el || !window.bootstrap) return;
        document.getElementById('copyToastText').textContent = text;
        bootstrap.Toast.getOrCreateInstance(el, { delay: 2200 }).show();
    }

    // Thả tim bài viết — cập nhật ngay, gửi lên server sau
    function initLikes() {
        document.querySelectorAll('[data-like]').forEach((btn) => {
            const count = btn.querySelector('[data-like-count]');
            btn.addEventListener('click', async () => {
                if (btn.disabled) return;
                btn.disabled = true;
                try {
                    const res = await fetch(btn.dataset.like, {
                        method: 'POST',
                        headers: { 'X-CSRF-Token': csrf },
                        credentials: 'same-origin',
                    });
                    if (!res.ok) throw new Error(res.status);
                    const data = await res.json();
                    count.textContent = data.likes;
                    btn.classList.toggle('is-liked', data.liked);
                    btn.setAttribute('aria-pressed', String(data.liked));
                    if (data.liked && !reduceMotion) {
                        btn.classList.remove('pop');
                        void btn.offsetWidth;          // chạy lại hiệu ứng
                        btn.classList.add('pop');
                    }
                } catch (_) {
                    toastSay('Không gửi được — tải lại trang rồi thử lại.');
                } finally {
                    btn.disabled = false;
                }
            });
        });
    }

    // Chia sẻ: điện thoại mở bảng chia sẻ của máy, máy tính thì chép link
    function initShare() {
        document.querySelectorAll('[data-share]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const url = location.href.split('#')[0];
                if (navigator.share) {
                    try { await navigator.share({ title: btn.dataset.title || document.title, url }); } catch (_) { /* người dùng huỷ */ }
                    return;
                }
                toastSay(await copyText(url) ? 'Đã chép link bài viết' : url);
            });
        });
    }

    // Hỏi lại trước khi xoá
    function initConfirm() {
        document.querySelectorAll('form[data-confirm]').forEach((form) => {
            form.addEventListener('submit', (e) => {
                if (!window.confirm(form.dataset.confirm)) e.preventDefault();
            });
        });
    }

    // Ô chọn ảnh: hiện số ảnh đã chọn, sáng lên khi kéo thả vào
    function initUpload() {
        document.querySelectorAll('.upload-drop').forEach((drop) => {
            const input = drop.querySelector('input[type=file]');
            const label = drop.querySelector('[data-file-label]');
            input.addEventListener('change', () => {
                const n = input.files.length;
                label.textContent = n ? `Đã chọn ${n} ảnh — bấm “Tải lên”` : 'Bấm để chọn ảnh, hoặc kéo thả vào đây';
            });
            ['dragenter', 'dragover'].forEach((t) => drop.addEventListener(t, () => drop.classList.add('is-over')));
            ['dragleave', 'drop'].forEach((t) => drop.addEventListener(t, () => drop.classList.remove('is-over')));
        });
    }

    // Đếm ký tự còn lại cho ô nhập dài
    function initCharCount() {
        document.querySelectorAll('textarea[data-counter][maxlength]').forEach((ta) => {
            const out = document.createElement('small');
            out.className = 'char-count';
            ta.after(out);
            const max = Number(ta.maxLength);
            const update = () => { out.textContent = `${ta.value.length} / ${max}`; };
            ta.addEventListener('input', update);
            update();
        });
    }

    /* ---------------------------------------------- 11. CHI TIẾT THEO SỞ THÍCH */
    // Timecode trong khung ngắm máy quay (giờ:phút:giây:khung hình, 30 khung/giây)
    function initTimecode() {
        const el = document.querySelector('[data-timecode]');
        if (!el) return;
        const start = performance.now();
        const pad = (n) => String(n).padStart(2, '0');
        const tick = () => {
            const f = Math.floor((performance.now() - start) / (1000 / 30));
            const s = Math.floor(f / 30);
            el.textContent = `${pad(Math.floor(s / 3600))}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}:${pad(f % 30)}`;
            if (!reduceMotion) requestAnimationFrame(tick);
        };
        tick();
    }

    // Gõ lệnh terminal từng ký tự (trang Dự án)
    function initTerminal() {
        const el = document.querySelector('.term-cmd[data-type]');
        if (!el || reduceMotion) return;
        const text = el.textContent;
        el.textContent = '';
        let i = 0;
        const type = () => {
            el.textContent = text.slice(0, ++i);
            if (i < text.length) setTimeout(type, 70 + Math.random() * 60);
        };
        setTimeout(type, 500);
    }

    /* ---------------------------------------------------------- KHỞI ĐỘNG */
    initNavScroll();
    initReveal();
    initTypewriter();
    initCounters();
    initLightbox();
    initCopy();
    initTheme();
    initScrollUi();
    initSpotlight();
    initHeroGlow();
    initCursor();
    initLikes();
    initShare();
    initConfirm();
    initUpload();
    initCharCount();
    initTimecode();
    initTerminal();
})();
