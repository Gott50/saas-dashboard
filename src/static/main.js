// custom javascript

var watch_job_ids = [];

function add_watcher(job_ids) {
    watch_job_ids = [...watch_job_ids, ...job_ids.filter(j=> !watch_job_ids.includes(j))]
}

function startWatcher() {
    getQueue();
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

function getStarted(res) {
    const html = `
        <div>${res.data.job_id}</div>
        <div>${JSON.stringify(res.data.job_meta)}</div>
        <div>${res.data.job_result}</div>
      `
    document.getElementById('started').innerHTML = html;
}

function getDefaultHTML(job) {
    return `
      <tr>
        <td>${job.job_id}</td>
        <td>${job.job_status}</td>
        <td>${job.job_result}</td>
        <td>${JSON.stringify(job.job_meta)}</td>
      </tr>`;
}

function getQueue() {
    $.ajax({
        url: `/jobs`,
        method: 'GET'
    })
        .done((res) => {
            const html = res.data.jobs.map(getDefaultHTML);
            document.getElementById('tasks').innerHTML = html;
        })
        .fail((err) => {
            console.error(err)
        });
}
