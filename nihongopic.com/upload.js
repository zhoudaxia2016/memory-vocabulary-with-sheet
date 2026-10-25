const fileId = 'TODO: 更换文件 ID';
const picUrl = 'https://img.qwps.cn/1510085126?imageMogr2/thumbnail/180x180!&1688082542448851145';
const filename = '头像';
const HTTPUrl = `https://www.kdocs.cn/api/v3/office/file/${fileId}/attachment`;

const result = HTTP.post(HTTPUrl, 
  {
    url: picUrl,
    local_cover: 'url',
    filename,
  },
  {
  headers: {
    'Content-Type': 'multipart/form-data',
    'Cookie': 'TODO: 自己填',
    'Origin': 'https://www.kdocs.cn',
  },
});
const resultText = result.text();
const object_id = JSON.parse(resultText).object_id;
console.log('resultText: ', resultText);

// const uploadId = 'TR24MBABLA';
console.log('object_id: ', object_id);
const records = Application.Record.UpdateRecords({
  SheetId: 8,
  Records: [{
    id: 'T2',
    fields: {
      "照片": [{
        "uploadId": object_id,
        "fileName": "照片.jpg",
        "source": 'upload_ks3',
        "type": "image/jpeg",
        "size": 4470,
        "imgSize": '180*180',
      }]
    }
  }],
})
