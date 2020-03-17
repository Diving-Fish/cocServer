package main

import (
	"github.com/kataras/iris/v12"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	"log"
)

func main() {
	session, err := mgo.Dial("mongodb://coc:SakuraYui@localhost:27017/coc")
	if err != nil {
		log.Fatal(err)
	}
	log.Print("successfully connect to db")
	playerData := session.DB("coc").C("playerData")
	pairData := session.DB("coc").C("pairs")
	server := iris.Default()
	crs := func(ctx iris.Context) {
		ctx.Header("Access-Control-Allow-Origin", "*")
		ctx.Header("Access-Control-Allow-Credentials", "true")
		ctx.Header("Access-Control-Allow-Headers", "Access-Control-Allow-Origin,Content-Type,Authorization")
		if ctx.Method() == "OPTIONS" {
			return
		}
		ctx.Next()
	}
	server.Use(crs)
	server.Options("*", func(ctx iris.Context) {
		ctx.Next()
	})
	server.Post("/insert", func(ctx iris.Context) {
		data := bson.M{}
		_ = ctx.ReadJSON(&data)
		_ = playerData.Insert(data)
	})
	server.Get("/query", func(ctx iris.Context) {
		name := ctx.URLParam("name")
		data := bson.M{}
		_ = playerData.Find(bson.M{"name": name}).One(&data)
		ctx.JSON(data)
	})
	server.Get("/show_all", func(ctx iris.Context) {
		pwd := ctx.URLParam("pwd")
		pwdPair := bson.M{}
		var players []bson.M
		_ = pairData.Find(bson.M{"key": "pwd"}).One(&pwdPair)
		if pwd == pwdPair["value"] {
			_ = playerData.Find(nil).All(&players)
			ctx.JSON(players)
		} else {
			ctx.StatusCode(401)
		}
	})
	server.Run(iris.Addr(":25565"))
}
