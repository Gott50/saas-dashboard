// custom javascript

var watch_job_ids = [];

function add_watcher(job_ids) {
    watch_job_ids = [...watch_job_ids, ...job_ids.filter(j=> !watch_job_ids.includes(j))]
}

function startWatcher() {
    requestJobsStatus(watch_job_ids, started);
    getQueue();
    setTimeout(startWatcher, 10000);
}

function requestJobsStatus(watch_job_ids, callback) {
    if (watch_job_ids.length <= 0) return;
    $.ajax({
        url: '/jobs/status',
        data: JSON.stringify(watch_job_ids),
        method: 'POST',
        contentType: 'application/json'
    })
        .done(callback)
        .fail((err) => {
            console.error(err)
        });
}

function started(res) {
    res.data.jobs.filter(job => job.job_status === 'started').forEach(getStarted);
    res.data.jobs.filter(job => job.job_status === 'finished').forEach(getFinished);
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

function getStartedHTML(job) {
    var question = '';
    var new_questions = '';
    if (job.job_meta) {
        if (job.job_meta.question) {
            question = `<h3>Question:</h3><code>${job.job_meta.question}</code>`
        }
        if (job.job_meta.new_questions) {
            new_questions = `<h3>New Questions:</h3>`
                + job.job_meta.new_questions.map(q => `<code>${q}<code/>`)
        }
    }
    return `
        <h2>${job.job_id}</h2>
        ${question}
        ${new_questions}
        <div>${job.job_result}</div>
      `;
}

function getStarted(job) {
    const html = getStartedHTML(job)
    document.getElementById('started').innerHTML = html;
}

function getFinished(job) {
    watch_job_ids = watch_job_ids.filter(id => id !== job.job_id);
    $('#finished').prepend(getStartedHTML(job));
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
            if(!res.data)
                return false;
            const html = res.data.jobs.map(getDefaultHTML).join("");
            document.getElementById('tasks').innerHTML = html;
        })
        .fail((err) => {
            console.error(err)
        });
}

function selectAll() {
    checkboxes = document.getElementsByClassName("checkbox");
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = true;
    }
}