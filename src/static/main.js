// custom javascript

$( document ).ready(() => {
  console.log('Sanity Check!');
});

function submit() {
  console.log($('form').serialize())
  $.ajax({
    url: '/user',
    data: $('form').serialize(),
    method: 'POST'
  })
      .done((res) => {
        res.data.job_ids.map(getStatus)
      })
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
    // setTimeout(function() {
    //   getStatus(jobID);
    // }, 1000);
  })
  .fail((err) => {
    console.log(err)
  });
}
