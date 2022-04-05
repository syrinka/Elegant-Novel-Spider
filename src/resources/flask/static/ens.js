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


function bind_filter_input() {
    $('#filter').on('keypress', function(e) {
        if (e.keyCode === 13) {
            apply_filter()
        }
    })
}


function dispatch() {
    var path = window.location.pathname
    if (path.startsWith('/shelf')) {
        bind_filter_input()
        update_shelf()
    } else if (path.startsWith('/chap')) {

    }
}
