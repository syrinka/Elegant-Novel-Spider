function apply_search() {
    const val = $('#searchbar').val()
    window.location.search = `?query=${encodeURI(val)}`
}


function bind_theme_switcher() {
    $('#theme-switcher').on('click', function(e){
        $('html').attr('data-theme',
            (index, attr) => {
                var theme = $.cookie('theme') == 'light' ? 'dark' : 'light'
                $.cookie('theme', theme, {path: '/'})
                return theme
            }
        )
    })
}


function bind_searchbar() {
    $('#searchbar').on('keypress', function(e){
        if (e.which === 13) {
            apply_search()
        }
    })
}


function bind_edge(){
    $('[id^=edge]').on('click', function(e){
        var href = $(this).attr('href')
        if (href) {
            window.location.pathname = href
        } else {
            alert('已经到底了！')
        }
    })

    $(document).on('keydown', function(e){
        if (e.which == 37) {
            $('#edge-prev').click()
        } else if (e.which == 39) {
            $('#edge-next').click()
        }
    })
}

$('html').attr('data-theme', $.cookie('theme') || 'light')

function dispatch() {
    bind_theme_switcher()
    const path = window.location.pathname
    if (path.startsWith('/shelf')) {
        bind_searchbar()
    } else if (path.startsWith('/chap')) {
        bind_edge()
    }
}
