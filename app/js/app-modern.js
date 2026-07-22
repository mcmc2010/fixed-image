$('.has-submenu > a').on('click', function(e) {
    e.preventDefault();
    const $parent = $(this).parent();
    const wasOpen = $parent.hasClass('open');
    $('.has-submenu').removeClass('open');
    if (!wasOpen) $parent.addClass('open');
});

$(document).on('click', function(e) {
    if (!$(e.target).closest('.has-submenu').length) {
        $('.has-submenu').removeClass('open');
    }
});

var pluginsLoaded = false;

window.addEventListener('pywebviewready', function() {
    if (pluginsLoaded) return;
    pluginsLoaded = true;
    window.pywebview.api.get_plugins().then(function(plugins) {
        var $list = $('#plugins-list');
        $list.empty();
        if (plugins.length === 0) {
            $list.append('<li><a href="#">无插件</a></li>');
        } else {
            plugins.forEach(function(p) {
                var label = p.name;
                if (p.version) label += ' v' + p.version;
                $list.append('<li><a href="#" class="plugin-item" data-name="' + p.name + '" title="' + (p.description || '') + '"><i class="bi bi-box"></i> ' + label + '</a></li>');
            });
        }
    });
});

$(document).on('click', '.plugin-item', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    var name = $(this).data('name');
    setTimeout(function() {
        window.pywebview.api.run_plugin(name).then(function(result) {
            if (result) {
                $('#status-text').text(result);
            }
        });
    }, 100);
});

$('#btn-open').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    openImage();
});

$('#btn-export').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    exportImage();
});

$('#btn-export-selection').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    exportSelection();
});

$('#btn-exit').on('click', function(e) {
    e.preventDefault();
    window.pywebview.api.close();
});

$('#btn-version').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    $('#versionModal').addClass('show');
});

$('#btn-resize').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    showResizeDialog();
});

$('#btn-restore').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    restoreOriginal();
});

$('#btn-bg').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    $('#bgModal').addClass('show');
});

$('#btn-remove-bg').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    showRemoveBgDialog();
});

$('#btn-feather').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    showFeatherDialog();
});

$('#versionModal').on('click', function(e) {
    if ($(e.target).is('#versionModal') || $(e.target).is('.modal-close')) {
        $(this).removeClass('show');
    }
});

$('#tb-open').on('click', function() {
    openImage();
});

$('#tb-save').on('click', function() {
    $('#status-text').text('已保存');
    setTimeout(function() { $('#status-text').text('就绪'); }, 2000);
});

var currentFilePath = '';
var zoomLevel = 100;
var originalWidth = 0;
var originalHeight = 0;

function updateZoom() {
    $('#status-zoom').text(zoomLevel + '%');
    $('#preview-img').css('transform', 'scale(' + (zoomLevel / 100) + ')');
}

$('#tb-zoom-in').on('click', function() {
    zoomLevel = Math.min(zoomLevel + 10, 500);
    updateZoom();
});

$('#tb-zoom-out').on('click', function() {
    zoomLevel = Math.max(zoomLevel - 10, 30);
    updateZoom();
});

$('#tb-zoom-reset').on('click', function() {
    zoomLevel = 100;
    updateZoom();
});

function openImage() {
    if (window.pywebview) {
        window.pywebview.api.open_file().then(function(result) {
            if (result) {
                if (result.path === currentFilePath) return;
                currentFilePath = result.path;
                zoomLevel = 100;
                updateZoom();
                $('#preview-img').attr('src', result.data).on('load', function() {
                    var w = this.naturalWidth;
                    var h = this.naturalHeight;
                    originalWidth = w;
                    originalHeight = h;
                    $('#status-size').text(w + ' × ' + h);
                    $('#status-original').hide();
                });
                $('#image-viewer').show();
                $('#welcome').hide();
                $('#status-text').text(result.path);
            }
        });
    } else {
        alert('需要在 pywebview 中运行');
    }
}

function exportImage() {
    var src = $('#preview-img').attr('src');
    if (!src) {
        alert('请先打开图片');
        return;
    }
    if (window.pywebview) {
        window.pywebview.api.get_export_path(currentFilePath).then(function(file_path) {
            if (file_path) {
                window.pywebview.api.check_file_exists(file_path).then(function(exists) {
                    if (exists) {
                        if (!confirm('文件已存在，是否覆盖？')) return;
                    }
                    window.pywebview.api.do_export(src, file_path).then(function(result) {
                        if (result) {
                            $('#status-text').text('已导出: ' + result);
                        }
                    });
                });
            }
        });
    }
}

function exportSelection() {
    var src = $('#preview-img').attr('src');
    if (!src) {
        alert('请先打开图片');
        return;
    }
    var rect = getSelectionRect();
    if (rect.w < 2 || rect.h < 2) {
        alert('请先选择区域');
        return;
    }
    var img = document.getElementById('preview-img');
    var canvas = document.getElementById('select-canvas');
    var imgRect = img.getBoundingClientRect();
    var canvasRect = canvas.getBoundingClientRect();
    var offsetX = imgRect.left - canvasRect.left;
    var offsetY = imgRect.top - canvasRect.top;
    var scaleX = img.naturalWidth / imgRect.width;
    var scaleY = img.naturalHeight / imgRect.height;
    var realX = Math.round((rect.x - offsetX) * scaleX);
    var realY = Math.round((rect.y - offsetY) * scaleY);
    var realW = Math.round(rect.w * scaleX);
    var realH = Math.round(rect.h * scaleY);
    if (window.pywebview) {
        var defaultName = currentFilePath ? currentFilePath.replace(/\.[^.]+$/, '') + '_clip' : 'clip';
        window.pywebview.api.get_export_path(defaultName).then(function(file_path) {
            if (file_path) {
                window.pywebview.api.check_file_exists(file_path).then(function(exists) {
                    if (exists) {
                        if (!confirm('文件已存在，是否覆盖？')) return;
                    }
                    window.pywebview.api.do_export_selection(src, file_path, realX, realY, realW, realH).then(function(result) {
                        if (result) {
                            $('#status-text').text('已导出选区: ' + result);
                        }
                    });
                });
            }
        });
    }
}

var aspectRatio = 1;

function showResizeDialog() {
    var img = document.getElementById('preview-img');
    if (!img.src) {
        alert('请先打开图片');
        return;
    }
    var w = img.naturalWidth;
    var h = img.naturalHeight;
    $('#resize-width').val(w);
    $('#resize-height').val(h);
    aspectRatio = w / h;
    $('#resizeModal').addClass('show');
}

$('#resize-width').on('input', function() {
    if ($('#resize-lock').is(':checked')) {
        var w = parseInt($(this).val());
        if (w > 0) {
            $('#resize-height').val(Math.round(w / aspectRatio));
        }
    }
});

$('#resize-height').on('input', function() {
    if ($('#resize-lock').is(':checked')) {
        var h = parseInt($(this).val());
        if (h > 0) {
            $('#resize-width').val(Math.round(h * aspectRatio));
        }
    }
});

$('#resize-ok').on('click', function() {
    var w = parseInt($('#resize-width').val());
    var h = parseInt($('#resize-height').val());
    if (w <= 0 || h <= 0) {
        alert('请输入有效的宽高');
        return;
    }
    var src = $('#preview-img').attr('src');
    window.pywebview.api.resize_image(src, w, h).then(function(result) {
        $('#preview-img').attr('src', result);
        $('#status-size').text(w + ' × ' + h);
        if (originalWidth > 0 && (w !== originalWidth || h !== originalHeight)) {
            $('#status-original').text('原始: ' + originalWidth + ' × ' + originalHeight).show();
        }
        $('#resizeModal').removeClass('show');
        $('#status-text').text('已调整大小');
    });
});

$('#resize-cancel').on('click', function() {
    $('#resizeModal').removeClass('show');
});

$('#resizeModal').on('click', function(e) {
    if ($(e.target).is('#resizeModal') || $(e.target).is('.modal-close')) {
        $(this).removeClass('show');
    }
});

function showRemoveBgDialog() {
    var img = document.getElementById('preview-img');
    if (!img.src) {
        alert('请先打开图片');
        return;
    }
    $('#removeBgModal').addClass('show');
}

$('#bg-color').on('input', function() {
    $('#bg-color-hex').text($(this).val());
});

$('#bg-tolerance').on('input', function() {
    $('#bg-tolerance-val').text($(this).val());
});

$('#remove-bg-ok').on('click', function() {
    var color = $('#bg-color').val();
    var tolerance = parseInt($('#bg-tolerance').val());
    var src = $('#preview-img').attr('src');
    window.pywebview.api.remove_background(src, color, tolerance).then(function(result) {
        if (result) {
            $('#preview-img').attr('src', result);
            $('#removeBgModal').removeClass('show');
            $('#status-text').text('已移除背景');
        }
    });
});

$('#remove-bg-cancel').on('click', function() {
    $('#removeBgModal').removeClass('show');
});

$('#removeBgModal').on('click', function(e) {
    if ($(e.target).is('#removeBgModal') || $(e.target).is('.modal-close')) {
        $(this).removeClass('show');
    }
});

$('.bg-option').on('click', function() {
    $('.bg-option').removeClass('active');
    $(this).addClass('active');
    var bg = $(this).data('bg');
    var $wrapper = $('#image-wrapper');
    $wrapper.removeAttr('style');
    if (bg === 'checkerboard') {
        $wrapper.addClass('checkerboard-bg');
    } else {
        $wrapper.removeClass('checkerboard-bg').css('background-color', bg);
    }
});

$('#bgModal').on('click', function(e) {
    if ($(e.target).is('#bgModal') || $(e.target).is('.modal-close')) {
        $(this).removeClass('show');
    }
});

function showFeatherDialog() {
    var img = document.getElementById('preview-img');
    if (!img.src) {
        alert('请先打开图片');
        return;
    }
    $('#featherModal').addClass('show');
}

$('#feather-radius').on('input', function() {
    $('#feather-radius-val').text($(this).val());
});

$('#feather-blur').on('input', function() {
    $('#feather-blur-val').text($(this).val());
});

$('#feather-ok').on('click', function() {
    var radius = parseInt($('#feather-radius').val());
    var blur = parseInt($('#feather-blur').val());
    var src = $('#preview-img').attr('src');
    window.pywebview.api.feather_image(src, radius, blur).then(function(result) {
        if (result) {
            $('#preview-img').attr('src', result);
            $('#featherModal').removeClass('show');
            $('#status-text').text('已羽化');
        }
    });
});

$('#feather-cancel').on('click', function() {
    $('#featherModal').removeClass('show');
});

$('#featherModal').on('click', function(e) {
    if ($(e.target).is('#featherModal') || $(e.target).is('.modal-close')) {
        $(this).removeClass('show');
    }
});

function restoreOriginal() {
    if (window.pywebview) {
        window.pywebview.api.restore_original().then(function(result) {
            if (result) {
                $('#preview-img').attr('src', result).on('load', function() {
                    var w = this.naturalWidth;
                    var h = this.naturalHeight;
                    $('#status-size').text(w + ' × ' + h);
                    $('#status-original').hide();
                });
                zoomLevel = 100;
                updateZoom();
                $('#status-text').text('已恢复原图');
            } else {
                alert('没有可恢复的原图');
            }
        });
    }
}

var selectMode = false;
var selecting = false;
var draggingHandle = null;
var draggingSelection = false;
var dragOffsetX = 0;
var dragOffsetY = 0;
var selectStartX = 0;
var selectStartY = 0;
var selectEndX = 0;
var selectEndY = 0;
var handleSize = 8;

$('#btn-select, #tb-select').on('click', function(e) {
    e.preventDefault();
    $('.has-submenu').removeClass('open');
    toggleSelectMode();
});

function toggleSelectMode() {
    selectMode = !selectMode;
    if (selectMode) {
        $('#select-canvas').show();
        $('#tb-select').addClass('active');
        $('#status-text').text('选择模式');
    } else {
        $('#select-canvas').hide();
        $('#tb-select').removeClass('active');
        clearSelection();
        $('#status-text').text('就绪');
    }
}

$('#select-canvas').on('mousedown', function(e) {
    if (!selectMode) return;
    var rect = this.getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;
    var sel = getSelectionRect();
    var handles = getHandles(sel.x, sel.y, sel.w, sel.h);
    draggingHandle = null;
    draggingSelection = false;
    for (var key in handles) {
        var hx = handles[key].x;
        var hy = handles[key].y;
        if (mx >= hx - handleSize && mx <= hx + handleSize && my >= hy - handleSize && my <= hy + handleSize) {
            draggingHandle = key;
            break;
        }
    }
    if (draggingHandle) {
        selecting = false;
    } else if (sel.w > 2 && sel.h > 2 && mx > sel.x && mx < sel.x + sel.w && my > sel.y && my < sel.y + sel.h) {
        draggingSelection = true;
        selecting = false;
        dragOffsetX = mx - sel.x;
        dragOffsetY = my - sel.y;
    } else {
        selecting = true;
        selectStartX = mx;
        selectStartY = my;
        selectEndX = mx;
        selectEndY = my;
    }
});

$('#select-canvas').on('mousemove', function(e) {
    if (!selectMode) return;
    var rect = this.getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;
    var sel = getSelectionRect();
    var handles = getHandles(sel.x, sel.y, sel.w, sel.h);
    var cursor = 'crosshair';
    for (var key in handles) {
        var hx = handles[key].x;
        var hy = handles[key].y;
        if (mx >= hx - handleSize && mx <= hx + handleSize && my >= hy - handleSize && my <= hy + handleSize) {
            if (key === 'tl' || key === 'br') cursor = 'nwse-resize';
            else cursor = 'nesw-resize';
            break;
        }
    }
    if (cursor === 'crosshair' && sel.w > 2 && sel.h > 2 && mx > sel.x && mx < sel.x + sel.w && my > sel.y && my < sel.y + sel.h) {
        cursor = 'move';
    }
    this.style.cursor = cursor;
});

$(document).on('mousemove', function(e) {
    var canvas = document.getElementById('select-canvas');
    if (!canvas) return;
    var rect = canvas.getBoundingClientRect();
    var mx = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    var my = Math.max(0, Math.min(e.clientY - rect.top, rect.height));
    if (selecting) {
        selectEndX = mx;
        selectEndY = my;
        drawSelection();
    } else if (draggingHandle) {
        if (draggingHandle === 'tl') { selectStartX = mx; selectStartY = my; }
        else if (draggingHandle === 'tr') { selectEndX = mx; selectStartY = my; }
        else if (draggingHandle === 'bl') { selectStartX = mx; selectEndY = my; }
        else if (draggingHandle === 'br') { selectEndX = mx; selectEndY = my; }
        drawSelection();
    } else if (draggingSelection) {
        var sel = getSelectionRect();
        var newX = mx - dragOffsetX;
        var newY = my - dragOffsetY;
        selectStartX = newX;
        selectStartY = newY;
        selectEndX = newX + sel.w;
        selectEndY = newY + sel.h;
        drawSelection();
    }
});

$(document).on('mouseup', function() {
    selecting = false;
    draggingHandle = null;
    draggingSelection = false;
    var sel = getSelectionRect();
    if (sel.w > 2 && sel.h > 2) {
        var img = document.getElementById('preview-img');
        var canvas = document.getElementById('select-canvas');
        if (img && canvas) {
            var imgRect = img.getBoundingClientRect();
            var canvasRect = canvas.getBoundingClientRect();
            var scaleX = img.naturalWidth / imgRect.width;
            var scaleY = img.naturalHeight / imgRect.height;
            var realW = Math.round(sel.w * scaleX);
            var realH = Math.round(sel.h * scaleY);
            $('#status-text').text('选择: ' + realW + '×' + realH);
        }
    }
});

function getHandles(x, y, w, h) {
    return {
        tl: { x: x, y: y },
        tr: { x: x + w, y: y },
        bl: { x: x, y: y + h },
        br: { x: x + w, y: y + h }
    };
}

function drawSelection() {
    var canvas = document.getElementById('select-canvas');
    var ctx = canvas.getContext('2d');
    var container = canvas.parentElement;
    canvas.width = container.scrollWidth;
    canvas.height = container.scrollHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    var sel = getSelectionRect();
    ctx.clearRect(sel.x, sel.y, sel.w, sel.h);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.strokeRect(sel.x, sel.y, sel.w, sel.h);
    var handles = getHandles(sel.x, sel.y, sel.w, sel.h);
    ctx.fillStyle = '#fff';
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.setLineDash([]);
    for (var key in handles) {
        ctx.fillRect(handles[key].x - handleSize / 2, handles[key].y - handleSize / 2, handleSize, handleSize);
        ctx.strokeRect(handles[key].x - handleSize / 2, handles[key].y - handleSize / 2, handleSize, handleSize);
    }
}

function clearSelection() {
    var canvas = document.getElementById('select-canvas');
    var ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function getSelectionRect() {
    var x = Math.min(selectStartX, selectEndX);
    var y = Math.min(selectStartY, selectEndY);
    var w = Math.abs(selectEndX - selectStartX);
    var h = Math.abs(selectEndY - selectStartY);
    return { x: x, y: y, w: w, h: h };
}
