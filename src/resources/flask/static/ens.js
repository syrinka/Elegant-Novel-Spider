function update_shelf(rules) {
    fetch('/search', {
        method: 'POST',
        body: JSON.stringify(rules || []),
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(response => response.json())
        .then(function(data) {
            const shelf = $('#shelf')
            shelf.html('')
            for (var info of data.infos) {
                shelf.append(` \
                    <a class="node" href="/novel/${info.remote}/${info.nid}"> \
                        ${info.title} \
                    </a> \
                `)
            }
        });
}


function apply_filter() {
    const val = $('#filter').val()
    if (val) {
        var rules = val.split(' ')
        for (let i in rules) {
            if (!rules[i].includes('=')) {
                rules[i] = 'title=' + rules[i]
            }
        }
        update_shelf(rules)
    } else {
        update_shelf()
    }
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


function bind_filter_input() {
    $('#filter').on('keypress', function(e){
        if (e.keyCode === 13) {
            apply_filter()
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

    } else if (path.startsWith('/chap')) {
        bind_edge()
    }
}
