const express = require('express');
const bodparser = require('body-parser')
const {spawn} = require('child_process');
const multer = require('multer')

const app = express();
const http = require('http');
const port = 5000;
const fs = require('fs');
const hostname = '192.168.4.107';
const path = require('path');
const { type } = require('os');
app.use(bodparser.json());
decision_lst = {'Forward\r\n':0, 'Left\r\n':0, 'Right\r\n':0};
const keys = Object.keys(decision_lst);

const server = http.createServer(app);
const io = require('socket.io')(server);

// console.log(keys);
var End_flag = true;
decision1 = 'why';
decision2 = 'me?';
counter = 0;
counter2 = 0;
const storage = multer.diskStorage({
    destination: function(req, file, cb) {
      cb(null, 'uploads/');
    },
    filename: function(req, file, cb) {
      cb(null,counter + file.originalname);
    }
});
app.use(express.static(__dirname+'/uploads'));
const upload = multer({storage: storage});
app.get('/', (req, res)=>{
    res.statusCode=200;
    res.send("get request to the root");
    console.log("GET req");
 
    let img = new Buffer.from(img_name, 'base64');
    fs.writeFileSync(path.join(path.dirname(require.main.filename),'uploads', counter+'photo.png'), img, err => {
      console.log('done');
    });
    python_logic('0photo.png');
    console.log('End');

});

var direction = 0;
var Directions = ["Stop","Forward","Right","Left"]
function python_logic(img_name){
  //console.log('in python')
  const python = spawn('python', ['detect.py', 'uploads/'+ img_name]);
  python.stdout.on('data', data =>{
    console.log(`processing image: ${img_name}`);
    direction = data;
    
    io.emit('result', "album.jpg");

  });
  python.on('close', code =>{

  });
}

app.get('/dola', (req, res) =>{
  //console.log("ESP Get Request");
  res.end(direction);
  console.log("Direction : " + Directions[parseInt(direction)]) 
  direction = 0
  });

app.get('/view', (req, res) =>{
  //console.log("ESP Get Request");
  res.sendFile(path.join(__dirname,'index.html'));
  io.emit('result', "album.jpg");


  });
  



app.post('/image',upload.single('fileData'), (req, res) =>{

    python_logic(req.file.filename);
    io.emit('image', req.file.filename);
    setTimeout(() => {
      res.status(200).end();
    }, 2000);


    counter++;

});



server.listen(5000, () => console.log(`server running at port: ${port}`));
