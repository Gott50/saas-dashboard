// custom javascript

var watch_job_ids = [];

function add_watcher(job_ids) {
    watch_job_ids = [...watch_job_ids, ...job_ids]
}

function startWatcher() {
    document.getElementById('tasks').innerHTML = '';
    watch_job_ids.map(getStatus);
    setTimeout(startWatcher, 1000);
}

$(document).ready(() => {
    console.log('startWatcher()');
    startWatcher()
});

function submit() {
    console.log($('form').serialize())
    $.ajax({
        url: '/user',
        data: $('form').serialize(),
        method: 'POST'
    })
        .done(res => add_watcher(res.data.job_ids))
        .fail((err) => {
            console.error(err)
        });
};

function getStatus(jobID) {
    $.ajax({
        url: `/jobs/${jobID}`,
        method: 'GET'
    })
        .done((res) => {
            const html = `
      <tr>
        <td>${res.data.job_id}</td>
        <td>${res.data.job_status}</td>
        <td>${res.data.job_result}</td>
        <td>${JSON.stringify(res.data.job_meta)}</td>
      </tr>`
            $('#tasks').prepend(html);
            const taskStatus = res.data.job_status;
            if (taskStatus === 'finished' || taskStatus === 'failed') return false;
        })
        .fail((err) => {
            console.error(err)
        });
}
