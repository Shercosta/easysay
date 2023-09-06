const express = require("express");
const bodyParser = require("body-parser");
const path = require("path");
const CSVToJSON = require("csvtojson");
const JSONToCSV = require("json2csv").parse;
var fs = require("fs");
const { PythonShell } = require("python-shell");
const multer = require("multer");

let bulkDocumentID;
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "./");
  },
  filename: (req, file, cb) => {
    bulkDocumentID = new Date().getMilliseconds();
    cb(null, bulkDocumentID + ".csv");
  },
});
const upload = multer({ storage: storage });

const app = express();

app.set("views", [path.join(__dirname, "views")]);
app.set("view engine", "ejs");

app.use(bodyParser.urlencoded({ extended: true, limit: "50mb" }));
app.use(express.static("public"));
app.use(express.json({ limit: "50mb" }));

app.get("/", (req, res) => {
  res.render("home/home");
});

app.get("/help", (req, res) => {
  res.render("help/help");
});

app.route("/option").post((req, res) => {
  const obj = {
    language: req.body.language,
    select: req.body.select,
  };
  if (obj.language === "Indonesia") {
    if (obj.select === "single") {
      res.render("indonesia/single", { language: obj.language });
    } else {
      res.render("indonesia/bulkJQuery");
    }
  } else if (obj.language === "Inggris") {
    if (obj.select === "single") {
      res.render("inggris/single");
    } else {
      res.render("inggris/bulk");
    }
  } else {
    res.redirect("/");
  }
});

app.post("/ens", (req, res) => {
  const keyAnswer = req.body.teacherAnswer;
  const answer = req.body.studentAnswer;
  const language = req.body.language;
  const docid = req.body.docid;

  let Dataset = `keyAnswer,studentAnswer\n"${keyAnswer}","${answer}"`;

  let scoreLoad;

  fs.writeFileSync(docid + ".csv", Dataset, "utf8");

  let options = {
    mode: "json",
    pythonOptions: ["-u"],
    args: [docid],
  };

  PythonShell.run("models/english/aprilModel.py", options)
    .then((messages) => {
      scoreLoad = messages;
    })
    .then(() => {
      fs.unlink(docid + ".csv", (err) => {
        //delete the csv file from crowding
        if (err) throw err;
      });
    })
    .then(() => {
      res.render("result/singleResult", {
        language: language,
        keyAnswer: scoreLoad[0].keyAnswer["0"],
        answer: scoreLoad[0].studentAnswer["0"],
        score: ((scoreLoad[0].scoreModelStem["0"] / 5) * 100).toFixed(2) + "%",
      });
    })
    .catch((err) => {
      res.render("result/singleResult", {
        language: language,
        keyAnswer: keyAnswer,
        answer: answer,
        score:
          "Submitted paragraphs may not contain meaningful words for the app to check, so we cannot continue the calculation",
      });
    });
});

app.post("/enb", upload.single("studentAnswers"), (req, res) => {
  const keyAnswer = req.body.teacherAnswer;
  const studentNames = req.body.nameColumns;
  const answerColumns = req.body.answerColumns;
  const language = req.body.language;
  let docid = bulkDocumentID;
  let scoreLoad;

  CSVToJSON()
    .fromFile("./" + docid + ".csv")
    .then((source) => {
      for (let i = 0; i < source.length; i++) {
        source[i].keyAnswer = keyAnswer;
        source[i].studentAnswer = source[i][answerColumns];
        source[i].studentName = source[i][studentNames];
      }
      const csv = JSONToCSV(source);
      fs.writeFileSync(docid + ".csv", csv);

      let options = {
        mode: "json",
        pythonOptions: ["-u"],
        args: [docid],
      };

      PythonShell.run("models/english/aprilModel.py", options)
        .then((messages) => {
          scoreLoad = messages;
        })
        .then(() => {
          fs.unlink(docid + ".csv", (err) => {
            if (err) throw err;
          });
        })
        .then(() => {
          res.render("result/bulkResult", {
            language: language,
            keyAnswer: keyAnswer,
            givenObjectKeyLength: Object.keys(scoreLoad[0].studentName).length,
            objectName: scoreLoad[0].studentName,
            objectAnswer: scoreLoad[0].studentAnswer,
            objectScore: scoreLoad[0].scoreModelStem,
          });
        });
    });
});

app.post("/ids", (req, res) => {
  const { language, teacherAnswer, studentAnswer, docid } = req.body;

  let option = {
    mode: "text",
    pythonOptions: ["-u"],
    args: [teacherAnswer, studentAnswer, docid],
  };

  PythonShell.run("./models/indonesia/ASAG.py", option).then((messages) => {
    let txtfile = fs
      .readFileSync(docid + ".txt", "utf-8")
      .replace(/\r/g, "")
      .split("\n");

    fs.unlink(docid + ".txt", (err) => {
      if (err) throw err;
    });
    res.render("result/singleResult", {
      language: language,
      keyAnswer: teacherAnswer,
      score: txtfile[0] + "%",
      answer: studentAnswer,
    });
  });
});

app.post("/idbulk", upload.single("studentAnswers"), async (req, res) => {
  const { teacherAnswer, nameColumns, answerColumns, language } = req.body;
  let docid = bulkDocumentID;

  let idbulk1 = fs.readFileSync("public/pages/bulkID1.html", "utf-8");
  let idbulk2 = fs.readFileSync("public/pages/bulkID2.html", "utf-8");
  let idbulk3 = fs.readFileSync("public/pages/bulkID3.html", "utf-8");

  res.write(idbulk1);
  res.write("<p>");
  res.write(teacherAnswer);
  res.write("</p>");
  res.write(idbulk2);

  const sources = await CSVToJSON().fromFile("./" + docid + ".csv");

  if (
    sources[0][nameColumns] == undefined &&
    sources[0][answerColumns] == undefined
  ) {
    fs.unlink(docid + ".csv", (err) => {
      if (err) throw err;
    });
    res.write(
      '<div class="alert alert-warning" role="alert">Kolom Nama dan / atau kolom jawaban pelajar sepertinya tidak cocok dengan apa yang ada di file CSV, mohon di cek lagi karena harus sama persis namanya</div>'
    );
    res.end();
  } else {
    for (i = 0; i < sources.length; i++) {
      sources[i].studentName = sources[i][nameColumns];
      sources[i].studentAnswer = sources[i][answerColumns];
    }
    for (let i = 0; i < sources.length; i++) {
      const options = {
        mode: "text",
        pythonOptions: ["-u"],
        args: [teacherAnswer, sources[i][answerColumns], docid],
      };
      await PythonShell.run("./models/indonesia/ASAGbulk.py", options).then(
        (messages, err) => {
          console.log("error LINE 267");
          res.write("<tr>");
          res.write("<td>");
          res.write(sources[i].studentName);
          res.write("</td>");
          res.write("<td>");
          res.write(sources[i].studentAnswer);
          res.write("</td>");
          res.write("<td>");
          res.write(messages[0]);
          res.write("</td>");
          res.write("</tr>");
          res.write("<br />");
        }
      );
    }
    res.write(idbulk3);
    fs.unlink(docid + ".csv", (err) => {
      if (err) throw err;
    });
    res.end();
  }
});

app.route("/ScenarioEn").post((req, res) => {
  const { key, ans } = req.body; //json recieved from postman has key and ans, put in their own variable

  let Dataset = `keyAnswer,studentAnswer\n"${key}","${ans}"`;

  fs.writeFileSync("ScenarioEn.csv", Dataset, "utf8");

  let options = {
    mode: "json",
    pythonOptions: ["-u"],
    args: ["ScenarioEn"],
  };

  PythonShell.run("models/english/aprilModel.py", options).then((messages) => {
    // res.send(((messages[0].scoreModelStem["0"] / 5) * 100).toFixed(2) + "%");
    // code above is to send just the score in a 0 to 100% percent range
    res.send(messages);
    // code above is to send the whole scoring processes as the model does
  });
});

app.route("/ScenarioEnTab").post((req, res) => {
  const { key } = req.body;

  CSVToJSON()
    .fromFile("./dataset.csv")
    .then((source) => {
      for (let i = 0; i < source.length; i++) {
        source[i].keyAnswer = key;
      }
      const csv = JSONToCSV(source);
      fs.writeFileSync("dataset.csv", csv);

      let options = {
        mode: "json",
        pythonOptions: ["-u"],
        args: ["dataset"],
      };

      PythonShell.run("models/english/aprilModelTab.py", options).then(
        (messages) => {
          res.send(messages[0].scoreModelStem);
          // res.send(messages);
        }
      );
    });
});

app.route("/ScenarioId").post((req, res) => {
  const { key, ans } = req.body; //json recieved from postman has key and ans, put in their own variable

  let option = {
    mode: "text",
    pythonOptions: ["-u"],
    args: [key, ans, "ScenarioId"],
  };

  PythonShell.run("./models/indonesia/ASAG.py", option).then((messages) => {
    let txtfile = fs
      .readFileSync("ScenarioId" + ".txt", "utf-8")
      .replace(/\r/g, "")
      .split("\n");

    fs.unlink("ScenarioId" + ".txt", (err) => {
      if (err) throw err;
    });
    res.send(txtfile[0] + "%");
  });
});

app.listen(process.env.PORT || 1234, () => {
  console.log("Listening to http://localhost:1234");
});
