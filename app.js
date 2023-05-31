var express = require('express');
var http = require('http');
var app = express();
var server = http.createServer(app).listen(80);
var mysql = require('mysql');
let database = "test";
var connection = mysql.createConnection({
  host: '127.0.0.1',
  user: 'root',
  password: '0000',
  database: 'injury'
});
connection.connect(console.log('연결'));

let { spawn } = require('child_process');
app.get('/test3', function (req, res) {
  const pythonProcess = spawn('python', ['test.py']);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python 프로세스 종료, 종료 코드: ${code}`);
    res.send("새로 불러왔습니다.");
  });
});

app.get('/home', function (req, res) {
  res.sendfile("home.html")
});
app.get('/test4', function (req, res) {
  res.sendfile("selectCar.html")
});
app.get('/find', function (req, res) {
    let findTitle = req.query.findTitle;
    connection.query(`SELECT * FROM team;`,
    function(error, result, fields){
    if (error) throw error
    else res.send(result);
    })
});
app.get('/team', function (req, res) {
    let teamName = req.query.teamName;
    console.log(teamName);
    connection.query(`SELECT * FROM ${teamName};`,
    function(error, result, fields){
    if (error) throw error
    else res.send(result);
    })
});
app.get('/part', function (req, res) {
    let teamName = req.query.teamName;
    console.log(teamName);
    connection.query(`SELECT distinct reason FROM entire;`,
    function(error, result, fields){
    if (error) throw error
    else res.send(result);
    })
});
app.get('/partChoice', function (req, res) {
    let reason = req.query.reason;
    console.log(reason);
    connection.query(`SELECT *  FROM entire where reason = "${reason}"`,
    function(error, result, fields){
    if (error) throw error
    else res.send(result);
    })
});
app.get('/teamAll', function (req, res) {
  res.sendfile("teamAll.html")
});
app.get('/injuryPart', function (req, res) {
  res.sendfile("injuryPart.html")
});
app.get('/teamSeperate', function (req, res) {
  res.sendfile("team.html")
});
