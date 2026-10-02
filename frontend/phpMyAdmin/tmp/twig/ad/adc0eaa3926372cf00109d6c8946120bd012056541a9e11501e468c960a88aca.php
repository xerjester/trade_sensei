<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* table/operations/view.twig */
class __TwigTemplate_42dc0b0a8a658a45590ec108e107f976f548cdff357e56c995db574acc6b8ac7 extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 1
        echo "<div class=\"container-fluid\">
  <form method=\"post\" action=\"";
        // line 2
        echo PhpMyAdmin\Url::getFromRoute("/view/operations");
        echo "\">
    ";
        // line 3
        echo PhpMyAdmin\Url::getHiddenInputs(($context["db"] ?? null), ($context["table"] ?? null));
        echo "
    <input type=\"hidden\" name=\"reload\" value=\"1\">
    <input type=\"hidden\" name=\"submitoptions\" value=\"1\">

    <div class=\"card mb-2\">
      <div class=\"card-header\">";
        // line 8
        echo _gettext("Operations");
        echo "</div>
      <div class=\"card-body\">
        <div class=\"form-inline\">
          <label for=\"newNameInput\">";
        // line 11
        echo _gettext("Rename view to");
        echo "</label>
          <input id=\"newNameInput\" class=\"form-control ml-2\" type=\"text\" name=\"new_name\" onfocus=\"this.select()\" value=\"";
        // line 12
        echo twig_escape_filter($this->env, ($context["table"] ?? null), "html", null, true);
        echo "\" required>
        </div>
      </div>
      <div class=\"card-footer text-right\">
        <input class=\"btn btn-primary\" type=\"submit\" value=\"";
        // line 16
        echo _gettext("Go");
        echo "\">
      </div>
    </div>
  </form>

  <div class=\"card mb-2\">
    <div class=\"card-header\">";
        // line 22
        echo _gettext("Delete data or table");
        echo "</div>
    <div class=\"card-body\">
      <div class=\"card-text\">
        ";
        // line 25
        echo PhpMyAdmin\Html\Generator::linkOrButton(PhpMyAdmin\Url::getFromRoute("/sql", twig_array_merge(        // line 26
($context["url_params"] ?? null), ["sql_query" => ("DROP VIEW " . PhpMyAdmin\Util::backquote(        // line 27
($context["table"] ?? null))), "goto" => PhpMyAdmin\Url::getFromRoute("/table/structure"), "reload" => true, "purge" => true, "message_to_show" => twig_escape_filter($this->env, sprintf(_gettext("View %s has been dropped."),         // line 31
($context["table"] ?? null))), "table" =>         // line 32
($context["table"] ?? null)])), _gettext("Delete the view (DROP)"), ["id" => "drop_view_anchor", "class" => "text-danger ajax"]);
        // line 39
        echo "
        ";
        // line 40
        echo \PhpMyAdmin\Html\MySQLDocumentation::show("DROP VIEW");
        echo "
      </div>
    </div>
  </div>
</div>
";
    }

    public function getTemplateName()
    {
        return "table/operations/view.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  93 => 40,  90 => 39,  88 => 32,  87 => 31,  86 => 27,  85 => 26,  84 => 25,  78 => 22,  69 => 16,  62 => 12,  58 => 11,  52 => 8,  44 => 3,  40 => 2,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "table/operations/view.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\table\\operations\\view.twig");
    }
}
