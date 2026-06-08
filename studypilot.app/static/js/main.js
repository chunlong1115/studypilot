/* ============================================
   智学伴 StudyPilot - JavaScript
   计时器 / AJAX / 交互逻辑
   ============================================ */

/* -------- 全局学习计时器 -------- */
var StudyTimer = {
    seconds: 0,
    intervalId: null,
    running: false,

    init: function () {
        var bar = document.getElementById('timerBar');
        if (!bar) return;
        // 恢复上午已记录的时间
        var saved = parseInt(localStorage.getItem('study_seconds_today') || '0');
        var savedDate = localStorage.getItem('study_date');
        var today = new Date().toDateString();
        if (savedDate !== today) {
            saved = 0;
            localStorage.setItem('study_date', today);
            localStorage.setItem('study_seconds_today', '0');
        }
        this.seconds = saved;
        this.render();
        this.updateDisplay();
    },

    start: function () {
        if (this.running) return;
        var self = this;
        this.running = true;
        this.intervalId = setInterval(function () {
            self.seconds++;
            self.updateDisplay();
            // 每 30 秒持久化一次
            if (self.seconds % 30 === 0) {
                localStorage.setItem('study_seconds_today', self.seconds.toString());
                localStorage.setItem('study_date', new Date().toDateString());
            }
        }, 1000);
        this.render();
    },

    pause: function () {
        if (!this.running) return;
        this.running = false;
        clearInterval(this.intervalId);
        this.intervalId = null;
        // 暂停时保存
        localStorage.setItem('study_seconds_today', this.seconds.toString());
        localStorage.setItem('study_date', new Date().toDateString());
        this.render();
        this.saveToServer();
    },

    saveToServer: function () {
        var minutes = Math.round(this.seconds / 60);
        if (minutes < 1) return;
        fetch('/api/study-time', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ minutes: minutes })
        }).catch(function () {});
    },

    updateDisplay: function () {
        var el = document.getElementById('timerValue');
        if (!el) return;
        var h = Math.floor(this.seconds / 3600);
        var m = Math.floor((this.seconds % 3600) / 60);
        var s = this.seconds % 60;
        el.textContent = String(h).padStart(2, '0') + ':' +
                         String(m).padStart(2, '0') + ':' +
                         String(s).padStart(2, '0');
    },

    render: function () {
        var btn = document.getElementById('timerBtn');
        if (!btn) return;
        if (this.running) {
            btn.innerHTML = '<i class="bi bi-pause-circle me-1"></i>暂停';
            btn.className = 'btn btn-timer running';
            btn.onclick = function () { StudyTimer.pause(); };
        } else {
            btn.innerHTML = '<i class="bi bi-play-circle me-1"></i>开始计时';
            btn.className = 'btn btn-timer';
            btn.onclick = function () { StudyTimer.start(); };
        }
    }
};

/* -------- AI 摘要生成 -------- */
function generateAISummary(materialId) {
    var area = document.getElementById('summaryArea');
    area.innerHTML = '<div class="py-2"><span class="spinner-border spinner-border-sm me-2" style="color:#4A90D9;"></span>AI 正在分析...</div>';

    fetch('/ai/generate-summary/' + materialId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (data.success) {
            area.innerHTML =
                '<div class="card border-0 shadow-sm mb-4" style="border-left:4px solid #4A90D9!important;">' +
                '<div class="card-body text-start">' +
                '<h6><i class="bi bi-robot me-1" style="color:#4A90D9;"></i>AI 摘要</h6>' +
                '<p class="mb-1">' + data.summary + '</p>' +
                (data.key_points ? '<p class="text-muted small mb-0">' + data.key_points + '</p>' : '') +
                '</div></div>';
        } else {
            area.innerHTML = '<div class="text-danger small py-2">' + data.message + '</div>';
        }
    })
    .catch(function () {
        area.innerHTML = '<div class="text-danger small py-2">AI 服务请求失败，请检查 API Key 配置。</div>';
    });
}

/* -------- 页面初始化 -------- */
document.addEventListener('DOMContentLoaded', function () {
    // 启动学习计时器
    StudyTimer.init();

    // 自动关闭 alert
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 5000);
    });
});
