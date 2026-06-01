/* ============================================
   智学伴 StudyPilot - 主要 JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
    // 自动关闭 alert
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 5000);
    });
});

/** AJAX 生成 AI 摘要 */
function generateAISummary(materialId) {
    var area = document.getElementById('summaryArea');
    area.innerHTML = '<div class="py-2"><span class="spinner-border spinner-border-sm me-2" style="color: #4A90D9;"></span>AI 正在分析中...</div>';

    fetch('/ai/generate-summary/' + materialId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (data.success) {
            area.innerHTML = '<div class="card border-0 shadow-sm mb-4" style="border-left: 4px solid #4A90D9 !important;">' +
                '<div class="card-body text-start">' +
                '<h6><i class="bi bi-robot me-1" style="color: #4A90D9;"></i>AI 摘要</h6>' +
                '<p class="mb-1">' + data.summary + '</p>' +
                (data.key_points ? '<p class="text-muted small mb-0">' + data.key_points + '</p>' : '') +
                '</div></div>';
        } else {
            area.innerHTML = '<div class="text-danger small py-2">' + data.message + '</div>';
        }
    })
    .catch(function () {
        area.innerHTML = '<div class="text-danger small py-2">AI 服务请求失败，请确保 DeepSeek API Key 已配置。</div>';
    });
}
